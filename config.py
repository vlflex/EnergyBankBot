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
# словари с сообщениями
messages_dict: dict[str, str | Template] = {
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