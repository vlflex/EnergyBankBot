from collections import namedtuple

TupleUser = namedtuple('User', ['id', 'pin', 'email', 'authorized'])

class User(TupleUser):
    # получение всех атрибутов
    def get(self):
        return (self.id, self.pin, self.email, self.authorized)