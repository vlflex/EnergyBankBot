from copy import copy

class Account:
    # инициализация объекта
    def __init__(self, sum: float, rate: float, fill: float = 0):
        try:
            self.__sum = float(sum)
            self.__rate = float(rate)
            self.__fill = float(fill)
        except ValueError as ve:
            print(ve)
            

    # свойство суммы счёта
    @property
    def sum(self):
        return self.__sum

    # обновление суммы
    @sum.setter
    def sum(self, value: float):
        try:
            self.__sum = float(value)
        except ValueError as ve:
            print(ve)
            

    # свойство ставки счёта
    @property
    def rate(self):
        return self.__rate

    @rate.setter
    def rate(self, value: float):
        try:
            self.__rate = float(value)
        except ValueError as ve:
            print(ve)
            

    # свойство ставка в виде коэффициента (ежемесячный множитель)
    @property
    def rate_coef(self):
        return 1 + ((self.__rate / 100) / 12)

    # свойство суммы пополнения
    @property
    def fill(self):
        return self.__fill
    # обновление суммы пополнения

    @fill.setter
    def fill(self, value):
        try:
            self.__fill = float(value)
        except ValueError as ve:
            print(ve)

    # пополнение счёта на сумму пополнения
    def fill_account(self):
        self.__sum += self.__fill

    # начисление процентов
    def interest_accrual(self):
        self.__sum *= self.rate_coef
