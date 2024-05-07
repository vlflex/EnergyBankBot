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
    'pay_transaction_sender': Template('Перевод средств на счет №$getter'),
    'pay_transaction_getter': Template('Получение средств со счета №$sender'),
    'pay_casino_dice_win': 'Выигрыш в кости',
    'pay_casino_dice_lose': 'Проигрыш в кости',
    'pay_casino_slot_win': 'Выигрыш в слоты',
    'pay_casino_slot_lose': 'Проигрыш в слоты',
    'pay_transaction_sender': Template('Перевод на №$getter'),
    'pay_transaction_getter': Template('Получение от №$sender'),
    'currency_choose': 'Выберите валюту',
    'currency_result': Template('Результат для <i>$other_name</i>:\n<b>$other_nominal</b> $other_currency\t=\t<b>$our_nominal</b> $our_currency'),
    'currency_error': 'Ошибка получения информации, пожалуйста, повторите запрос',
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
    'calc_choose_data': f'Выберите искомые данные, где\n' 
                '<i>Количество месяцев</i> - срок погашения кредита или достижения цели по вкладу\n'\
                '<i>Суммая пополнения</i> - минимальная ежемесячная сумма пополнения счета для погашения кредита или достижении цели за некоторый срок',
    'calc_input_goal': 'Введите цель по вкладу',
    'calc_input_goal': 'Введите цель по вкладу',
    'calc_input_goal_greater_sum': Template('Ошибка: цель по вкладу должна быть больше текущей суммы ($sum)'),
    'calc_choose_data': f'Выберите искомые данные, где\n' 
                '<i>Количество месяцев</i> - срок погашения кредита или достижения цели по вкладу\n'\
                '<i>Суммая пополнения</i> - минимальная ежемесячная сумма пополнения счета для погашения кредита или достижения цели за некоторый срок',
    'calc_marker': '💰',
    'calc_inputed_data': 'Введенные данные:',
    'calc_start_sum': 'Начальная сумма ',
    'calc_fill': 'Ежемесячное пополнение ',
    'calc_months': 'Количество месяцев ',
    'calc_rate': 'Ставка счета ',
    'calc_goal': 'Цель по вкладу',
    'calc_month_result': Template('Месяцев необходимо: $months'),
    'calc_fill_result': Template('Требуемая сумма пополенения: $fill'),
    'calc_error': 'Ошибка: вычисление невозможно, начисляемые проценты превышают сумму пополнения',
    'casino_greet':'Велкам ту казик',
    'casino_nomoney':'А денег хватит?',
    'help': 'Введите ключевое слово или краткий вопрос по которому вы хотите получить ответ',
    'casino_input_bet':'Введите сумму ставки',
    'casino_no_bet':'Делаем ставки',
    'casino_bet_accepted': 'Ставка принята',
    'casino_bet_zero': 'Ошибка: нулевая ставка',
    'casino_noenough': Template('Недостаточно средств\nСтавка: <b>$bet</b>\nБаланс: <b>$balance</b>'),
    'casino_invalid_bet': 'Ошибка ввода ставки, введите число',
    'casino_dice_input': Template(f'Выберите число от 1 до 6 или чет/нечет\nКоэффициенты:\n<b>x$num</b> - для числа\n<b>x$even</b> - для чет/нечет'),
    'casino_dice_fail_input': 'Ошибка ввода: введите число от 1 до 6',
    'casino_choice_accepted': 'Выбор сохранён',
    'casino_win':Template('Выигрыш: $win\nСтавка $bet'),
    'casino_lose':Template('Проигрыш: $bet'),
    'casino_bet_more_balance': Template('Ошибка: ставка $bet больше средств на счёте: /balance'),
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
    'help': 'Помощь🆘',
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
    'casino_slot': 'Крутка🎰',
    'casino_dice': 'Кость🎲',
    'casino_bet': 'Ставка💰',
    'casino_dice_choice': 'Выбрать число🔢',
}

stickers_dict: Dict[str, str] = {
    'want_money': 'CAACAgIAAxkBAAIDmGYfAQGV7JgSKjSILbZZSr2peZsMAAITAAMhjG8wHCJ69Mnh5AY0BA',
    'cat_ask': 'CAACAgEAAxkBAAIDm2YfAVDdk95-n-67N9N-u7GOmAL0AAIVAwACDtepRzU9ZbtrpXoXNAQ',
    'only_money': 'CAACAgIAAxkBAAIDnWYfAXt3Y0YwBgLmyxVLoU-05wy5AAJfEgACjHIpS8kqH_1IJSH5NAQ',

}
photos_dict: Dict[str, str] = {
    'e_mouth': 'AgACAgIAAxkBAAIDJWYe9aBtToHKzmDrpBrjA8LW-FmcAALk2DEbN6f4SLPNh74lqAoAAQEAAwIAA3gAAzQE',
    'pig': 'AgACAgIAAxkBAAIDJ2Ye9g8or7RRzJgq3yUYYKgghGGxAALn2DEbN6f4SPccPtJdPSzqAQADAgADeQADNAQ',
    'pigs': 'AgACAgIAAxkBAAIDKWYe9i7lX0L0heUxPYnpqok1uajmAALo2DEbN6f4SEOJ5bSje5P5AQADAgADeQADNAQ',
    'python': 'AgACAgIAAxkBAAIDK2Ye9ngaHgYolx40mW8cQp5AxzVqAALp2DEbN6f4SJcN8AlW6JP_AQADAgADbQADNAQ',
    'bad': 'AgACAgIAAxkBAAIDLWYe9oc9z3R-kTWHkkOEosQKeGo2AALq2DEbN6f4SPhv4qIj1wVXAQADAgADeQADNAQ',
    'anime': 'AgACAgIAAxkBAAIDL2Ye9u3qA7-VWDQs0ucCV6N7qoVIAALr2DEbN6f4SDQWbfgMNMc0AQADAgADeQADNAQ',
    'think': 'AgACAgIAAxkBAAIDMWYe9wpOmiQba8qjtww_uxon0CC3AALs2DEbN6f4SKz_pwrquqJDAQADAgADbQADNAQ',
    'china': 'AgACAgIAAxkBAAIDWGYe99TmZpBQYx99Cfypw2jM1au-AALz1TEb5Xz4SJn_PXfRxf78AQADAgADeQADNAQ',
    'f_nv': 'AgACAgIAAxkBAAIDWmYe-FGLVod9nS6oPCV1ZSJfe9ZkAALt2DEbN6f4SCYh0AhDU0NQAQADAgADeQADNAQ',
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

try_photos: Dict[str, str] = {
    'stonks':'AgACAgIAAxkBAAIE52YfqQPk6iDnlymVmEGwFIvEsab1AAKU3jEbWTMBSXsUdlzlbJerAQADAgADeAADNAQ',
    'not_stonks':'AgACAgIAAxkBAAIE6WYfqUW_WoNXCFSgPisHygFYorvBAAKV3jEbWTMBST3cdBD9iTXGAQADAgADeAADNAQ',
    'ultra_stonks': 'AgACAgIAAxkBAAIE62YfqXRRs8IzeO0afZa-SQ2vK1DiAAKW3jEbWTMBSfk8hTPbYkCrAQADAgADbQADNAQ',
}

questions_dict: Dict[str, str] = {
    'Как открыть счет в EnergyBank?': 'Для открытия счета в EnergyBank вы можете заполнить заявку онлайн на нашем сайте или посетить ближайшее отделение.',
    'Какие документы нужны для открытия счета?': 'Для открытия счета вам понадобится действующий паспорт и документ, подтверждающий ваше место жительства.',
    'Какие виды счетов предлагает EnergyBank?': 'EnergyBank предлагает различные виды счетов, включая текущие счета, сберегательные счета и депозитные счета.',
    'Как получить кредит в EnergyBank?': 'Для получения кредита в EnergyBank вы можете заполнить заявку онлайн или обратиться в ближайшее отделение банка.',
    'Как узнать баланс на счете?': 'Чтобы узнать текущий баланс, вы можете воспользоваться командой /balance',
    'Как погасить кредит?': 'Погасить кредит можно через интернет-банкинг, в отделении банка или через терминалы самообслуживания.',
    'Какие возможности для инвестирования предлагает EnergyBank?': 'EnergyBank предлагает различные инвестиционные продукты, такие как ценные бумаги, инвестиционные фонды и пенсионные планы',
    'Какие процентные ставки на вклады?': 'Процентные ставки на вклады могут изменяться в зависимости от срока и типа вклада. Подробную информацию можно узнать на нашем сайте или в отделении банка.',
    'Как получить кредитную карту?': '	Для получения кредитной карты от EnergyBank вы можете заполнить заявку онлайн или обратиться в отделение банка.',
    'Как заблокировать карту?': 'Вы можете заблокировать карту, позвонив в наш контактный центр или воспользовавшись сайтом.',
    'Как изменить персональные данные?': 'Чтобы изменить персональные данные, вы можете воспользоваться интернет-банкингом или обратиться в отделение банка.',
    'Что делать, если забыл пароль от интернет-банкинга?': 'Если вы забыли пароль, вы можете сбросить его, следуя инструкциям на нашем сайте или обратившись в контактный центр.',
    'Как получить выписку по счету?': 'Вы можете заказать выписку по счету через интернет-банкинг, мобильное приложение или обратиться в отделение банка.',
    'Какие комиссии у EnergyBank?': 'Комиссии могут различаться в зависимости от услуги. Детальную информацию можно найти на нашем сайте или в отделении банка.',
    'Где получить консультацию по продуктам и услугам?': 'Вы можете получить консультацию в отделении банка, через онлайн-чат на нашем сайте или позвонив в контактный центр.',
    'Как отменить перевод денег?': 'Если перевод еще не обработан, вы можете отменить его через интернет-банкинг или обратившись в контактный центр.',
    'Как узнать статус кредитной заявки?': 'Вы можете узнать статус вашей кредитной заявки, связавшись с нашим контактным центром или посетив ближайшее отделение банка.',
    'Как подать жалобу?': 'Вы можете подать жалобу через интернет-банкинг, письменно или устно в отделении банка.',
    'Какие курсы валют?': 'Для получение информации о курсе валют вы можете воспользовать командой /currency (источник ЦБ РФ)',
    'Как сменить PIN-код карты?': 'Вы можете сменить PIN-код карты через команду /settings или в отделении банка.',
    'Что делать при утере карты?': 'При утере карты следует незамедлительно заблокировать ее. Вы можете сделать это через оффициальный сайт или позвонив в контактный центр.',
    'Как перевести деньги на другой счет?': 'Для перевода денег на другой счет вы можете воспользоваться интернет-банкингом или обратиться в отделение банка.',
    'Как пополнить счет через банкомат?': 'Вы можете пополнить счет через банкомат, используя карту или наличные.',
    'Как снять наличные со счета?': 'Для снятия наличных со счета вы можете воспользоваться банкоматом или обратиться в отделение банка.',
    'Какая минимальная сумма для открытия счета?': 'Минимальная сумма для открытия счета зависит от типа счета. Подробную информацию можно уточнить на нашем сайте или в отделении банка.',
    'Как узнать расписание работы отделения?': 'Расписание работы отделения можно узнать на нашем сайте или позвонив в контактный центр.',
    'Что делать, если у меня проблемы с доступом к интернет-банкингу?': 'Если у вас возникли проблемы с доступом к интернет-банкингу, свяжитесь с нашим контактным центром для получения помощи.',
    'Как проверить историю транзакций?': 'Вы можете проверить историю транзакций через интернет-банкинг или использовать команду /history',
    'Какие дополнительные услуги предлагает EnergyBank?': 'EnergyBank предлагает широкий спектр дополнительных услуг, включая страхование, ипотечное кредитование и пенсионное обеспечение.',
}

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