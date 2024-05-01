from copy import copy

class Account:
    # инициализация объекта
    def __init__(self, sum: float, rate: float, fill: float = 0):
        self.__sum = sum
        self.__rate = rate
        self.__fill = fill

    # свойство суммы счёта
    @property
    def sum(self):
        return self.__sum

    # обновление суммы
    @sum.setter
    def sum(self, value: float):
        self.__sum = float(value)
        
    # свойство ставки счёта
    @property
    def rate(self):
        return self.__rate

    @rate.setter
    def rate(self, value: float):
        self.__rate = float(value)
        
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
        self.__fill = float(value)

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
        return self.sum <= 0

    # получение мин. суммы пополнения для погашения кредина за months месяцев
    def get_fill_to_paid(self, months: int):
        months = int(months)
        fill = int(self.sum / months - 1)
        # создание временного объекта для симуляции ежемесячной платы
        tempAccount = copy(self)
        while (not tempAccount.is_paid()):
            fill += 10
            tempAccount = copy(self)
            tempAccount.fill = fill
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
        self.__goal = float(goal)

    # свойство цели по вкладу
    @property
    def goal(self):
        return self.__goal

    @goal.setter
    # обновление цели по вкладу
    def goal(self, value: float):
        self.__goal = float(value)

    # проверка: была ли достигнута цель (goal)
    def is_achieved(self):
        return self.sum >= self.__goal

    # получение мин. суммы пополнения для достижения цели
    def get_fill_to_achieve(self, months: int):
        fill = int((self.__goal - self.sum) / (months + 2))
        # создание временного объекта для симуляции ежемесячной платы
        tempAccount = copy(self)
        while (not tempAccount.is_achieved()):
            fill += 10
            tempAccount = copy(self)
            tempAccount.fill = fill
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