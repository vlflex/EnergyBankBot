import psycopg2 as psql
from psycopg2 import extensions as psql_ext
from psycopg2.errors import Error as PSQLerror

from collections import namedtuple
from typing import Tuple
from logging import DEBUG, INFO

from sys import path
path.append('D:/Университет/Учебная практика/Bank bot/') 
from config import config, LOG_LEVEL, get_ciphered, get_unciphered
from modules.logger import Logger
# настройка логгера
local_log = Logger('database', 'D:/Университет/Учебная практика/Bank bot/log/database.log', level=LOG_LEVEL)
# класс, соответствующий полям записи в БД
ClientRow = namedtuple('ClientRow', ['id', 'pincode', 'email', 'authorized', 'balance'])

class DataBase():
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
            return ClientRow(*result)
        else:
            local_log.warning(f'Can not select row (id={id}): it has not been found')
    # добавление записи
    # @local_log.wrapper(arg_level=DEBUG, res_level=DEBUG)
    def add(self, id: int, pincode: int | None = None, email: str | None = None, authorized: bool = False, balance: float = 0):
        if not self.select(id):
            pincode = get_ciphered(str(pincode)) if pincode else pincode # type: ignore
            self.__cur.execute("""--sql
                            INSERT INTO 
                                clients(id, pincode, email, authorized, balance)
                            VALUES 
                                (%s, %s, %s, %s, %s)
                            """, (id, pincode, email, authorized, balance))
            self.__conn.commit()
        else:
            local_log.warning('Can not ADD database row, it has already located in the database')
    
    # обновление записи
    @local_log.wrapper(arg_level=INFO, res_level=DEBUG)
    def update(self, id: int, pincode: int | None = None, email: str | None = None, authorized: bool = False, balance: float = 0):   # type: ignore
        if self.select(id):
            pincode = get_ciphered(str(pincode)) if pincode else pincode # type: ignore
            self.__cur.execute("""--sql
                            UPDATE 
                                clients
                            SET
                                pincode = %s,
                                email = %s,
                                authorized = %s,
                                balance = %s
                            WHERE 
                                id = %s""", (pincode, email, authorized, balance, id)) 
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
        assert not(results), "Table is empty"
        return tuple(ClientRow(*row) for row in results) # type: ignore
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.__name})'

class DataBaseException(Exception):
    """DataBase base exception
    """
    def __init__(self, message: str):
        self.__message = message
        super().__init__(self.__message)
        
class DataBaseConnectionException(DataBaseException):
    def __init__(self, message):
        super().__init__(message)