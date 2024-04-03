import logging as log
from functools import wraps

class Logger(log.Logger):
    def __init__(self, 
                module: str,
                filename: str,
                filemode: str = 'w',
                level: int = log.INFO,
                format: str = "%(asctime)s %(name)s\t%(funcName)s %(levelname)s %(message)s"):
        super().__init__(module)
        self.__init_handler(log.FileHandler(filename, filemode))
        self.__init_formatter(log.Formatter(format))
        self.setLevel(level)
    
    # установка хэндлера
    def __init_handler(self, handler: log.FileHandler):
        self.addHandler(handler)
        self.__handler = handler
        
    # установка формата
    def __init_formatter(self, formatter: log.Formatter):
        self.__handler.setFormatter(formatter)
        self.__init_handler(self.__handler)
    
    # декоратор для функций
    def wrapper(self, arg_level = log.INFO, res_level = log.INFO):
        def local_wrapper(func):
            # обновление формата (для вывода корректного названия функции или метода)
            self.__init_formatter(log.Formatter(f"%(asctime)s %(name)s\t{func.__name__} %(levelname)s %(message)s"))
            
            @wraps(func)
            def logged_func(*args, **kwargs):
                # выбор типа информирования
                _arg_note_func = self.debug if arg_level <= log.DEBUG else self.info
                _res_not_func = self.debug if res_level <= log.DEBUG else self.info
                # информация об аргументах функции
                _arg_note_func(f'Args: {args if args else ""}; {kwargs if kwargs else ""}')

                result = None
                try:
                    result = func(*args, **kwargs)
                except Exception as error:
                    self.exception(error)
                else:
                    _res_not_func(f'Return {result}')
                return result
            return logged_func
        return local_wrapper
    
if __name__ == '__main__':
    l = Logger('module', 'example.log', level=log.DEBUG)
    
    @l.wrapper(log.DEBUG, log.INFO)   # type: ignore
    def func(a, b):
        return a + b
    print(func('a', 'b'))
    