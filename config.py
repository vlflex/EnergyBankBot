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
    bot_url: SecretStr
    code_key: SecretStr
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
messages_dict: Dict[str, str | Template] = {
    'greet': Template(f'Здравствуйте, $name! Выберите желаемое действие'),
    'unauth_greet': Template(f'Здравствуйте, $name! Вы не авторизованы, выберите желаемое действие: '),
    'reg_offer': 'Кажется, вы не зарегистрированы, хотите пройти регистрацию?',
    'auth_offer': 'Кажется, вы уже зарегистрированы, хотите войти в аккаунт?',
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