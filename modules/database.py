import psycopg2 as psql
from psycopg2 import extensions as psql_ext
from psycopg2.errors import Error as PSQLerror

from typing import Tuple, NamedTuple, Sequence
from logging import DEBUG, INFO
import datetime as dt
from decimal import Decimal
from prettytable import PrettyTable

from sys import path
path.append('D:/Университет/Учебная практика/Bank bot/') 
import config as conf
from config import config, LOG_LEVEL, get_ciphered, get_unciphered
from modules.logger import Logger
# настройка логгера
local_log = Logger('database', f'{conf.PATH}/log/database.log', level=LOG_LEVEL)
# класс, соответствующий полям записи в БД
class ClientRow(NamedTuple):
    id: int
    pincode: int | None
    email: str | None
    authorized: bool
    balance: Decimal
    reg_date: dt.date | None
    
# класс для управлениями транзакциями
class TransactionRow(NamedTuple):
    id: int
    type: str
    client_id: int
    source: str
    amount: Decimal 
    date: dt.datetime
    desc: str | None

class DataBase():
    DEBIT_ID = 1
    ACCRUAL_ID = 2
    # виды списания/начисления
    TRANSFER_ID = 1
    CASINO_ID = 2
    
    # инициализация (по пути)
    def __init__(self, name: str):
        self.__name: str = name
        self.__conn: psql_ext.connection
        self.__cur: psql_ext.cursor
    # вход, подключение к бд
    def __enter__(self):
        try:
            self.__conn = psql.connect(
                dbname=self.__name,
                user=config.db_user.get_secret_value(),
                password=config.db_pass.get_secret_value(),
                host=config.db_host.get_secret_value(),
                port=config.db_port.get_secret_value()
            )  
            # type: ignore
            self.__cur = self.__conn.cursor()
        except PSQLerror as error: 
            local_log.exception(f'Can not connect to database:\n{error}')
            raise DataBaseConnectionException(str(error))
        else:
            return self
    # выход, отключение от бд
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__cur.close()
        self.__conn.close() 
    # свойство для получение курсора
    @property
    def cur(self):
        return self.__cur
    
    # поиск клиента
    @local_log.wrapper(arg_level=DEBUG, res_level=DEBUG)
    def select(self, id: int) -> ClientRow | None:
        self.__cur.execute("""--sql
                SELECT *
                FROM 
                    clients
                WHERE 
                    id = %s""", (id,))
        result = self.__cur.fetchone()
        if result:
            return self.__uncipher_client(ClientRow(*result))
        else:
            local_log.warning(f'Can not select row (id={id}): it has not been found')
    # добавление записи
    @local_log.wrapper(arg_level=INFO, res_level=DEBUG)
    def add(self, id: int, pincode: int | None = None, email: str | None = None, authorized: bool = False, balance: float = 0, reg_date: dt.date | None = None):
        if not self.select(id):
            pincode = get_ciphered(str(pincode)) if pincode else pincode # type: ignore
            email = get_ciphered(str(email)) if email else email # type: ignore
            self.__cur.execute("""--sql
                            INSERT INTO 
                                clients(id, pincode, email, authorized, balance, reg_date)
                            VALUES 
                                (%s, %s, %s, %s, %s, %s)
                            """, (id, pincode, email, authorized, balance, reg_date))
            self.__conn.commit()
        else:
            local_log.warning('Can not ADD database row, it has already located in the database')
    
    # обновление записи
    @local_log.wrapper(arg_level=INFO, res_level=DEBUG)
    def update(self, id: int, pincode: int | None = None, email: str | None = None, authorized: bool = False, balance: float = None, reg_date: dt.date | None = None):   # type: ignore
        old_client = self.select(id)
        if old_client:
            # если аргумент равен None, то присваивается значение из БД
            pincode = old_client.pincode if pincode is None else pincode
            email = old_client.email if email is None else email
            authorized = old_client.authorized if not authorized else authorized
            balance = old_client.balance if balance is None else balance    # type: ignore
            reg_date = old_client.reg_date if reg_date is None else reg_date
            # шифрование пинкода и почты
            pincode = get_ciphered(str(pincode)) if pincode else pincode # type: ignore
            email = get_ciphered(str(email)) if email else email # type: ignore
            
            self.__cur.execute("""--sql
                            UPDATE 
                                clients
                            SET
                                pincode = %s,
                                email = %s,
                                authorized = %s,
                                balance = %s,
                                reg_date = %s
                            WHERE 
                                id = %s""", (pincode, email, authorized, balance, reg_date, id)) 
            self.__conn.commit()
        else:
            local_log.warning('Can not UPDATE database, row has not found in the database')
            
    # получение всех записей
    @local_log.wrapper(DEBUG, DEBUG)
    def select_all(self) -> Tuple[ClientRow]:
        self.__cur.execute("""--sql
                SELECT *
                FROM 
                    clients
                """)
        results = self.__cur.fetchall()
        unchip_clients_tuple = tuple(self.__uncipher_client(ClientRow(*row)) for row in results)
        return unchip_clients_tuple # type: ignore
    
    # поиск транзакции
    @local_log.wrapper(arg_level=DEBUG, res_level=DEBUG)
    def select_trans(self, id: int) -> TransactionRow | None:
        self.__cur.execute("""--sql
                SELECT *
                FROM 
                    transactions_full
                WHERE 
                    id = %s""", (id,))
        result = self.__cur.fetchone()
        if result:
            return TransactionRow(*result)
        else:
            local_log.warning(f'Can not select row (id={id}): it has not been found')
        
    # добавление записи
    @local_log.wrapper(arg_level=INFO, res_level=DEBUG)
    def add_trans(self, 
            type_id: int,  
            client_id: int, 
            source_id: int, 
            amount: Decimal, 
            date: dt.datetime,
            desc: str | None = None, 
            ):
        
        # type_id не соответствует сумме транзакции
        if (type_id == self.DEBIT_ID and amount > 0) or (type_id == self.ACCRUAL_ID and amount < 0):
            raise InvalidTransactionException(f'type_id is not suitable for amount:\ntype_id:{type_id}\tamount:{amount}')
        # пропуск нулевых транзакций 
        elif amount == 0:
            return
        
        self.__cur.execute('''--sql
                        INSERT INTO 
                            transactions(type_id, client_id, source_id, amount, "date", "desc")
                        VALUES 
                            (%s, %s, %s, %s, %s, %s)
                        ''', (type_id, client_id, source_id, amount, date, desc))
        self.__conn.commit()
    
    # получение всех записей
    @local_log.wrapper(DEBUG, DEBUG)
    def select_all_trans(self) -> Tuple[TransactionRow]:
        self.__cur.execute("""--sql
                SELECT *
                FROM 
                    transactions_full
                """)
        results = self.__cur.fetchall()
        transation_row_tuple = tuple(TransactionRow(*row) for row in results)
        return transation_row_tuple # type: ignore
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.__name})'
    
    # получение последних транзакций клиента
    @local_log.wrapper(DEBUG, DEBUG)
    def select_client_trans(self, client_id: int) -> Tuple[TransactionRow]:
        self.__cur.execute("""--sql
            SELECT *
            FROM 
                transactions_full
            WHERE client_id = %s
            ORDER BY "date" DESC
        """, (client_id,))
        results = self.__cur.fetchall()
        transaction_row_tuple = tuple(self.__extract_trans_date(TransactionRow(*row)) for row in results)
        return transaction_row_tuple # type: ignore

    # заменяет строковое значение поля объекта-транзакции date на datetime объект
    @staticmethod
    @local_log.wrapper(DEBUG, DEBUG)
    def __extract_trans_date(trans: TransactionRow) -> TransactionRow:
        if isinstance(trans.date, str):
            return trans._replace(date=dt.datetime.strptime(trans.date, conf.TRANS_DATE_SQL_FORMAT)) # type: ignore
        else:
            return trans

    # декодирование pin и email из записи клиента
    @staticmethod
    @local_log.wrapper(DEBUG, DEBUG)
    def __uncipher_client(client: ClientRow) -> ClientRow:
        unciph_client = client._replace(
            pincode=get_unciphered(str(client.pincode)) if client.pincode else client.pincode,
            email = get_unciphered(client.email) if client.email else client.email
            )
        return unciph_client
    
    # создание таблицы для отображения транзакций
    @staticmethod
    @local_log.wrapper(DEBUG, DEBUG)
    def generate_trans_table(trans_seq: Sequence[TransactionRow]) -> str:
        table = PrettyTable()
        table.field_names = conf.TRANS_TABLE_HEADERS
        for trans in trans_seq:
            formated_date =  trans.date.strftime(conf.TRANS_DATE_FORMAT)
            formated_amount = f'{trans.amount:,}'
            table.add_row([formated_amount, formated_date, trans.desc])
        return str(table)

class DataBaseException(Exception):
    """DataBase base exception
    """
    def __init__(self, message: str):
        self.__message = message
        super().__init__(self.__message)
        
class DataBaseConnectionException(DataBaseException):
    def __init__(self, message):
        super().__init__(message)
        
class TransactionException(DataBaseException):
    def __init__(self, message):
        super().__init__(message)
        
class InvalidTransactionException(TransactionException):
    def __init__(self, message):
        super().__init__(message)