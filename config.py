from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from cryptography.fernet import Fernet
from string import Template
from logging import DEBUG, INFO
from typing import Dict, List

class Settings(BaseSettings):
    bot_token: SecretStr
    email: SecretStr
    password: SecretStr
    domain: SecretStr
    port: SecretStr
    code_key: SecretStr
    bot_url: SecretStr
    db_name: SecretStr
    db_user: SecretStr
    db_pass: SecretStr
    db_host: SecretStr
    db_port: SecretStr
    model_config = SettingsConfigDict(env_file = 'data/.env', 
                                    env_file_encoding = 'utf-8')
    
config = Settings() # type: ignore

# общая настройка уровня логгирования 
LOG_LEVEL =  INFO
# путь к директории
PATH = 'D:/Университет/Учебная практика/Bank bot'
# таймер между отправками email code (sec)
CODE_COOLDOWN = 180
# число попыток до блокировки
CODE_ATTEMPTS = 5

# URL для получение информации о курсе валют
CURRENCY_QUERY_URL = f'http://www.cbr.ru/scripts/XML_daily.asp'
# рубль
RUB = 'RUB🇷🇺'
# максимальный номинал, при котором делится курс
MAX_NOMINAL = 100

# количество записей на странице истории транзакций
TRANS_PAGE_COUNT = 10
# формат даты для просмотра итории
TRANS_DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
# формат даты в PSQL
TRANS_DATE_SQL_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
# заголовки для таблицы транзакций
TRANS_TABLE_HEADERS = ["Тип", 'Сумма', 'Источник', 'Дата', 'Описание']

# словари с сообщениями
messages_dict: Dict[str, str | Template] = {
    'greet': Template(f'Здравствуйте, $name! Выберите желаемое действие'),
    'unauth_greet': Template(f'Здравствуйте, $name! Вы не авторизованы, выберите желаемое действие: '),
    'reg_offer': 'Кажется, вы не зарегистрированы, хотите пройти регистрацию?',
    'reg_success': 'Регистрация успешно завершена! Используйте /start для входа',
    'reg_fail': 'Ошибка регистрации, кажется что-то пошло не так:()',
    'auth_offer': 'Кажется, вы уже зарегистрированы, хотите войти в аккаунт?',
    'pin_request': 'Введите pin-code',
    'pin_create': 'Придумайте pin-code из 4 цифр, он будет использоваться при авторизации',
    'invalid_pin': 'Неверный pin-code, попробуйте еще раз',
    'email_request': 'Введите email для получения кода:',
    'email_accepted': 'Email принят',
    'invalid_email': 'Неверный email, попробуйте ещё раз',
    'code_send': 'На введенный email был отправлен код подтверждения',
    'code_request': 'Введите полученный код из 6 цифр',
    'code_error': 'Ошибка отправки кода, попробуйте ещё раз или введите новый email',
    'code_accepted': 'Код подтверждения принят',
    'invalid_code': 'Неверный код, попробуйте ещё раз',
    'restore_success': 'Вы успешно восстановили pin-code. Используйте /start для входа',
    'restore_fail': 'Ошибка сброса pin-кода, кажется что-то пошло не так:()',
    'multiple_invalid_code': Template(f'Вы ввели код неверно {CODE_ATTEMPTS} раз. Начните заново с /start. Или попробуйте ввести код снова через: <b>$time</b>'),
    'multiple_invalid_pin': Template(f'Вы ввели pin-код неверно {CODE_ATTEMPTS} раз.\nВы можете восстановить pin-code, через email (будет отправлен код подтверждения).\nЛибо попробуйте ввести код снова через: <b>$time</b>'),
    'menu_balance': Template(f'Ваш баланс: <b>$balance₽</b>'),  # type: ignore
    'command_refuse': 'Вы не можете использовать эту комманду до авторизации. Используйте /start',
    'pay_target_choice': 'Нажмите на кнопку ниже для выбора получателя платежа',
    'pay_self_refuse': 'Ошибка: вы не можете совершить платеж себе',
    'pay_target_no_client': 'Ошибка: выбранный пользователь не является клиентов нашего банка',
    'pay_target_accepted': 'Данный пользователь доступен для перевода средств',
    'pay_amount': 'Введите сумму платежа',
    'pay_input_invalid': 'Ошибка ввода, введите сумму для перевода',
    'pay_input_nomoney': 'Ошибка перевода: на вашем счете недостаточно средств: /balance',
    'pay_attempt': 'Попытка совершение платежа..',
    'pay_input_success': 'Платеж успешно выполнен',
    'pay_input_fail': 'Ошибка платежа: кажется что-то пошло не так:()',
    'pay_transaction_sender': Template('Перевод средств на счет №$getter'),
    'pay_transaction_getter': Template('Получение средств со счета №$sender'),
    'currency_choose': 'Выберите валюту',
    'currency_result': Template('Результат для <i>$other_name</i>:\n<b>$other_nominal</b> $other_currency\t=\t<b>$our_nominal</b> $our_currency'),
    'currency_error': 'Ошибка получения информации, пожалуйста, повторите запрос',\
    'currency_input': 'Введите название валюты из 3 букв (например "USD")',
    'currency_input_fail': 'Ошибка: данные о валюте не были найдены',
    'currency_rub': 'Ошибка: нельзя получить курс рубля в рублях',
}
# функция для создания словаря для передачи в email форму
def create_email_form(email: str, code: int, registration: bool = True) -> Dict[str, str]:
    email_form: Dict[str, str] = {
        'from_field':'EnergyBank',
        'target_email':email,
        'subject':'Код подтверждения электронной почты',
        'text':
            f'Кто-то пытается подтвердить данный адрес для регистрации через <a href = {config.bot_url.get_secret_value()}>telegram бота</a><br>Код подтверждения: <h1>{code}</h1>' if registration else
            f'Кто-то пытается восстановить доступ к аккаунту с помощью вашего email через <a href = {config.bot_url.get_secret_value()}>telegram бота</a><br>Код подтверждения: <h1>{code}</h1>'
    }
    return email_form

buttons_dict: Dict[str, str] = {
    'reg': 'Регистрация',
    'auth': 'Авторизация',
    'send_code': 'Отправить код',
    'input_email': 'Ввести email',
    'input_pin': 'Ввести pin-код',
    'email_restore': 'Восстановить через email',
    'pay': 'Перевод💱',
    'pay_target': 'Выбрать получателя💳',
    'balance': 'Баланс💰',
    'history': 'История💸',
    'currency': 'Валюты💲',
    'calculator': 'Калькулятор🧮',
    'settings': 'Настройки⚙',
    'menu': 'Меню🧩',
    'curency_other': 'Другие валюты',
}

# словарь для хранения кодировок валют
currencies_dict: Dict[str, str] = {
    'USD':'USD🇺🇸',
    'EUR':'EUR🇪🇺',
    'CNY':'CNY🇨🇳',
    'INR':'INR🇮🇳',
    'UAH':'UAH🇺🇦',
    'BYN':'BYN🇧🇾',
    'KZT':'KZT🇰🇿',
    'UZS':'UZS🇺🇿',
    'JPY':'JPY🇯🇵',
    'GBP':'GBP🇬🇧',
    'AED':'AED🇦🇪',
    'TRY':'TRY🇹🇷',
}

commands_list: List[str] = [
    "balance",
    "history",
    "pay",  
    "settings",
    "currency",
    "calculator",
]
# шифрование данных
def get_ciphered(data: str):
    """Ciphere the data"""
    data = data.encode('utf-8') # type: ignore
    # получение ключа
    key = config.code_key.get_secret_value()
    # Инициализация объекта Fernet с ключом
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(data).decode('utf-8') # type: ignore

# дешифрование данных
def get_unciphered(cipherde_data: str):
    """Unciphere the data"""
    # получение ключа
    key = config.code_key.get_secret_value()
    # Инициализация объекта Fernet с ключом
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(cipherde_data).decode('utf-8')