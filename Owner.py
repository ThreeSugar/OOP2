class Owner:
    def __init__(self, name, email):
        self._name = name
        self._email = email

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self):
        self._email = email

    

