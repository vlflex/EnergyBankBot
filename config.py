from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    bot_token: SecretStr
    email: SecretStr
    password: SecretStr
    code_key: SecretStr
    model_config = SettingsConfigDict(env_file = '.env', 
                                    env_file_encoding = 'utf-8')
    
config = Settings() # type: ignore

# шифрование данных
def get_ciphered(data: str):
    data = data.encode('utf-8') # type: ignore
    # получение ключа
    key = config.code_key.get_secret_value()
    # Инициализация объекта Fernet с ключом
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(data).decode('utf-8') # type: ignore

# дешифрование данных
def get_unciphered(cipherde_data: str):
    # получение ключа
    key = config.code_key.get_secret_value()
    # Инициализация объекта Fernet с ключом
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(cipherde_data).decode('utf-8')