class Phone:
    count = 0
    def __init__(self, number, owner):
        self._number = number
        self._owner = owner
        self.__class__.count += 1

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        self._owner = owner


def reset_count():
    Phone.count = 0












