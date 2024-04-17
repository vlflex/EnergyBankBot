from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from cryptography.fernet import Fernet
from string import Template
from logging import DEBUG, INFO
from typing import Dict

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
    'casino_greet':'Велкам ту казик',
    'casino_nomoney':'А денег хватит?',
    'casino_input_bet':'Введите сумму ставки',
    'casino_no_bet':'Делаем ставки',
    'casino_bet_accepted': 'Ставка принята',
    'casino_noenough': Template('Недостаточно средств\nСтавка: <b>$bet</b>\nБаланс: <b>$balance</b>'),
    'casino_invalid_bet': 'Ошибка ввода ставки, введите число',
    'casino_dice_input': 'Выберите число от 1 до 6',
    'casino_dice_fail_input': 'Ошибка ввода: введите число от 1 до 6',
    'casino_choice_accepted': 'Выбор сохранён',
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

try_photos: Dict[str, str] = {
    'stonks':'AgACAgIAAxkBAAIE52YfqQPk6iDnlymVmEGwFIvEsab1AAKU3jEbWTMBSXsUdlzlbJerAQADAgADeAADNAQ',
    'not_stonks':'AgACAgIAAxkBAAIE6WYfqUW_WoNXCFSgPisHygFYorvBAAKV3jEbWTMBST3cdBD9iTXGAQADAgADeAADNAQ',
    'ultra_stonks': 'AgACAgIAAxkBAAIE62YfqXRRs8IzeO0afZa-SQ2vK1DiAAKW3jEbWTMBSfk8hTPbYkCrAQADAgADbQADNAQ',
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