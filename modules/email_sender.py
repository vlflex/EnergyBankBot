import smtplib as smtp
from smtplib import SMTPException
from email.message import EmailMessage
from email.headerregistry import Address
from email.errors import MessageError

from logging import DEBUG, INFO

from sys import path
path.append('D:/Университет/Учебная практика/Bank bot') 
import config as conf
from config import config, PATH
from logger import Logger

local_log = Logger('email_sender', f'{conf.PATH}/log/email_sender.log', level=conf.LOG_LEVEL)

class EmailSender:
    def __init__(self):
        self.__email: str
        self.__pass: str
        self.__server: smtp.SMTP
    
    # подключение к серверу 
    def __enter__(self):
        try:
            self.__email = config.email.get_secret_value()
            self.__pass = config.password.get_secret_value()
            _domain = config.domain.get_secret_value()
            _port = int(config.port.get_secret_value())
            self.__server = smtp.SMTP(f'smtp.{_domain}', _port)
            self.__server.starttls()
            self.__server.login(self.__email, self.__pass)
        except SMTPException as error:
            local_log.exception(f'SMTP error\n{error}')
        except Exception as error:
            local_log.exception(f'Unexpected exception\n{error}')
        return self
        
    # отключение от сервера
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__server.quit()
    
    # получение email
    @property
    def email(self):
        return self.__email
        
    # отправка сообщения
    @local_log.wrapper(arg_level=INFO, res_level=DEBUG)
    def send(self, from_field: str, target_email: str, subject: str, text: str):
        try:
            # создаем письмо
            msg = EmailMessage()
            msg.set_content(text, subtype='html')
            msg['Subject'] = subject
            email_name, domain = self.__email.split('@')
            msg['From'] = Address(from_field, email_name, domain)
            msg['To'] = target_email
            # отправка
            self.__server.send_message(msg)
        except MessageError as error:
            local_log.exception(f'Create email error\n{error}')
        except SMTPException as error:
            local_log.exception(f'Sending email error: {error}')
        except Exception as error:
            local_log.exception(f'Unexpected exception\n{error}')
        
    def __repr__(self):
        return f'{self.__class__.__name__}({self.__email}, {"*" * len(self.__pass)}, {self.__server} )'