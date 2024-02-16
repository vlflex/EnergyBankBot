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
    # стандартное сообщение при выводе
    def __repr__(self):
        return f'{__class__.__name__}({self.__sum}, {self.__rate}, {self.__fill})'
    
class CreditAccount(Account):
    # инициализация объекта
    def __init__(self, sum: float, rate: float, fill: float):
        Account.__init__(self, sum, rate, fill)

    # плата по кредиту
    def fill_account(self):
        self.sum -= self.fill

    # проверка: оплачен ли кредитный счёт
    def is_paid(self):
        if (self.sum <= 0):
            return True
        else:
            return False

    # получение мин. суммы пополнения для погашения кредина за months месяцев
    def get_fill_to_paid(self, months: int):

        try:
            months = int(months)
            fill = self.sum / months - 1
        except ValueError as ve:
            print(ve)
        else:
            tempAccount = copy(self)
            # создание временного объекта для симуляции ежемесячной платы

            while (not tempAccount.is_paid()):
                fill += 1
                tempAccount = copy(self)
                for i in range(months):
                    tempAccount.interest_accrual()
                    tempAccount.fill_account()
            else:
                return fill

    # получения кол-ва месяцев для выплаты кредита (при текущем пополнении)
    def get_months_to_paid(self):
        months = round(self.sum / self.fill) - 1
        # создание временного объекта для симуляции ежемесячной платы
        tempAccount = copy(self)
        while (not tempAccount.is_paid()):
            months += 1
            tempAccount = copy(self)

            for i in range(months):
                tempAccount.interest_accrual()
                tempAccount.fill_account()
        else:
            return months

    # копирование класса
    def __copy__(self):
        prefab = CreditAccount(self.sum, self.rate, self.fill)
        return prefab
    # стандартное сообщение при выводе
    def __repr__(self):
        return f'{__class__.__name__}({self.sum}, {self.rate}, {self.fill})'

class DepositAccount(Account):
    # инициализация объекта
    def __init__(self, sum: float, rate: float, fill: float, goal: float):
        Account.__init__(self, sum, rate, fill)

        try:
            self.__goal = float(goal)
        except ValueError as ve:
            print(ve)

    # свойство цели по вкладу
    @property
    def goal(self):
        return self.__goal

    @goal.setter
    # обновление цели по вкладу
    def goal(self, value: float):
        try:
            self.__goal = float(value)
        except ValueError as ve:
            print(ve)

    # проверка: была ли достигнута цель (goal)
    def is_achieved(self):
        if (self.sum >= self.__goal):
            return True
        else:
            return False

    # получение мин. суммы пополнения для достижения цели
    def get_fill_to_achieve(self, months: int):
        try:
            months = int(months)
            fill = (self.__goal - self.sum) / (months + 2)
        except ValueError as ve:
            print(ve)
        else:
            # создание временного объекта для симуляции ежемесячной платы
            tempAccount = copy(self)
            while (not tempAccount.is_achieved()):
                fill += 1
                tempAccount = copy(self)
                for i in range(months):
                    tempAccount.interest_accrual()
                    tempAccount.fill_account()
            else:
                return fill

    # получения кол-ва месяцев для достижения цели (при текущем пополнении)
    def get_months_to_achieve(self):
        months = int((self.__goal - self.sum) /
                     (self.fill)) // 2
        # создание временного объекта для симуляции ежемесячной платы
        tempAccount = copy(self)
        while (not tempAccount.is_achieved()):
            months += 1
            tempAccount = copy(self)
            for i in range(months):
                tempAccount.interest_accrual()
                tempAccount.fill_account()
        else:
            return months

    # копирование класса
    def __copy__(self):
        prefab = DepositAccount(self.sum,
                                self.rate,
                                self.fill,
                                self.__goal)
        return prefab
    
    # стандартное сообщение при выводе
    def __repr__(self):
        return f'{__class__.__name__}({self.sum}, {self.rate}, {self.fill}, {self.goal})'
    