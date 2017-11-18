class Beverage:
    def __init__(self, name, calories):
        self.__name = name
        self.__calories = calories

    def get_name(self):
        return self.__name

    def display_calories(self):
        print(self.__name, 'has calories', self.__calories)

    def get_calories(self):
        return self.__calories

    def __str__(self):
        return '{} has {} calories'.format(self.__name, self.__calories)


class Lemonade(Beverage):
    def __init__(self, price):
        super().__init__(name='Lemonade', calories='100')
        self.__price = price

    def __str__(self):
        return '{} has {} calories and cost {}'.format(super().get_name(), super().get_calories(), self.__price)


drink = Lemonade(1.5)
drink.display_calories()
print(drink)


