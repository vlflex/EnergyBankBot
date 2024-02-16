class User:
    # инициализация
    def __init__(self, id: int, pin: str = None, email: str = None, authorized: bool = False):    # type: ignore
        self.__id: int = id
        self.__pin: str = pin   # type: ignore
        self.__email: str = email   #  type: ignore
        self.__authorized: bool = authorized
    # свойство для получение id
    @property
    def id(self):
        return self.__id
    # id setter
    @id.setter
    def id(self, value: int):
        self.__id = value
    # свойство для получение pin
    @property
    def pin(self):
        return self.__pin
    # pin setter
    @pin.setter
    def pin(self, value: str):
        self.__pin = value
    # свойство для получение email
    @property
    def email(self):
        return self.__email
    # email setter
    @email.setter
    def email(self, value: str):
        self.__email = value
    # свойство для получение authorized
    @property
    def authorized(self):
        return self.__authorized
    # email setter
    @authorized.setter
    def authorized(self, value: bool):
        self.__authorized = value
    # получение информации
    def __repr__(self):
        return f'{__class__.__name__}({self.id}, {self.pin}, {self.email}, {self.authorized})'
    # получение всех атрибутов
    def get(self):
        return (self.id, self.pin, self.email, self.authorized)