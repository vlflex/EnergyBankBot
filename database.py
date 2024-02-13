import sqlite3 as sql
class DataBase():
    # инициализация (по пути)
    def __init__(self, src: str):
        self.__src: str = src
        self.__conn: sql.Connection = None
        self.__cur: sql.Cursor = None
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

