import sqlite3 as sql
from user import User
class DataBase():
    # инициализация (по пути)
    def __init__(self, src: str):
        self.__src: str = src
        self.__conn: sql.Connection = None # type: ignore
        self.__cur: sql.Cursor = None # type: ignore
    # вход, подключение к бд
    def __enter__(self):
        self.__conn = sql.connect(self.__src)
        self.__cur = self.__conn.cursor()
        return self
    # выход, отключение от бд
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__conn.commit()
        self.__conn.close() 
    # свойство для получение курсора
    @property
    def cur(self):
        return self.__cur
    # добавление пользователя
    def add_user(self, user: User): 
        with DataBase(self.__src) as db:
            db.cur.execute("""--sql
                            INSERT INTO Clients(id, pincode, email, authorized)
                            VALUES(?, ?, ?, ?)
                            """, 
                            tuple(user.get()),
                            )
    # получение данных о пользователе
    def get_user(self, id: int):
        with DataBase(self.__src) as db:
            db.cur.execute("""--sql
                            SELECT *
                            FROM Clients
                            WHERE id = ?
                            """,
                            (id,) 
                            )
            return User(*db.cur.fetchone())
    # редактирование пользователя
    def edit_user(self, user: User): 
        with DataBase(self.__src) as db:
            db.cur.execute("""--sql
                            UPDATE Clients
                            SET pincode = ?, email = ?, authorized = ?
                            WHERE id = ?
                            """, 
                            (user.pin, user.email, user.authorized, user.id) # type: ignore
                            )
    # получение всех id пользователей
    def get_all_id(self):
        with DataBase(self.__src) as db:
            db.cur.execute("""--sql
                            SELECT id
                            FROM Clients
                            """
                            )
            return db.cur.fetchall()
    # получение данных о всех пользователей
    def get_all_users(self):
        with DataBase(self.__src) as db:
            db.cur.execute("""--sql
                            SELECT *
                            FROM Clients
                            """
                            )
            return db.cur.fetchall()

