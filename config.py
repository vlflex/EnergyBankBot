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
TRANS_TABLE_HEADERS = ['Сумма', '            Дата                  ', '           Описание           ']

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
    'pay_input_invalid': 'Ошибка ввода, введите положительную сумму для перевода',
    'pay_input_nomoney': 'Ошибка перевода: на вашем счете недостаточно средств: /balance',
    'pay_attempt': 'Попытка совершение платежа..',
    'pay_sender_success': 'Платеж успешно выполнен',
    'pay_getter_success': Template('🔔Уведомление:\nПеревод средств в размере <b>$amount₽</b> от $sender\nНастройка уведомлений: /settings'),
    'pay_input_fail': 'Ошибка платежа: кажется что-то пошло не так:()',
    'pay_transaction_sender': Template('Перевод на №$getter'),
    'pay_transaction_getter': Template('Получение от №$sender'),
    'currency_choose': 'Выберите валюту',
    'currency_result': Template('Результат для <i>$other_name</i>:\n<b>$other_nominal</b> $other_currency\t=\t<b>$our_nominal</b> $our_currency'),
    'currency_error': 'Ошибка получения информации, пожалуйста, повторите запрос',
    'currency_input': 'Введите название валюты из 3 букв (например "USD")',
    'currency_input_fail': 'Ошибка: данные о валюте не были найдены',
    'currency_rub': 'Ошибка: нельзя получить курс рубля в рублях',
    'history_first_page': 'Текущая страница - первая',
    'history_last_page': 'Текущая страница - последняя',
    'history_empty': 'Вы ещё не совершили ни одной транзакции',
    'sets_updates': 'Настройки обновлены',
    'sets_choose': 'Выберите один из пунктов:',
    'sets_exit_warning': 'Вы действительно хотите выйти из аккаунта? Вам придется пройти авторизацию для доступа к аккаунту: /start',
    'sets_nots_error': 'Ошибка при обновлении данных',
    'calc_choose': 'Выберите тип счета для вычислений',
    'calc_input_positive_fail': 'Ошибка ввода: введите положительное число',
    'calc_input_notnegative_fail': 'Ошибка ввода: введите неотрицательное число',
    'calc_input_sum': 'Введите сумму на счете',
    'calc_input_rate': 'Введите процентную ставку',
    'calc_input_rate_fail': 'Ошибка ввода: введите положительное число, дробная часть разделяется точкой или запятой',
    'calc_input_months': 'Введите количество месяцев', 
    'calc_input_fill': 'Введите ежемесячное пополнение',
    'calc_input_goal': 'Введите цель по вкладу',
    'calc_choose_data': f'Выберите искомые данные, где\n' 
                '<i>Количество месяцев</i> - срок погашения кредита или достижения цели по вкладу\n'\
                '<i>Суммая пополнения</i> - минимальная ежемесячная сумма пополнения счета для погашения кредита или достижении цели за некоторый срок',
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
    'sets_nots_on': 'Уведомления✅',
    'sets_nots_off': 'Уведомления❌',
    'sets_pincode': 'Сменить pin-code🔑',
    'sets_exit': 'Выход🚪',
    'calc_credit': 'Кредит',
    'calc_deposite': 'Вклад',
    'calc_months': 'Количество месяцев',
    'calc_fill': 'Сумма пополнения',
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