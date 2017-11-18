class Beverage:
    def __init__(self, name, price):
        self.__name = name
        self.__price = price

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price


class Cocktail(Beverage):
    def __init__(self, name, alcohol, price):
        super().__init__(name, price)
        self.__alcohol = alcohol

    def get_alcohol(self):
        return self.__alcohol

    def __str__(self):
        return '{} with {} of alcohol at {}'.format(self.get_name(), self.get_alcohol(), self.get_price())


class Mocktail(Beverage):
    def __init__(self, name, price):
        super().__init__(name, price)

    def __str__(self):
        return '{} at {}'.format(self.get_name(), self.get_price())


class Bar:
    beverage = []
    orders = []

    @staticmethod
    def add_beverage(*args):
        for b in args:
            Bar.beverage.append(b)

    @staticmethod
    def add_orders(*args):
        for b in args:
            Bar.orders.append(b)


    def create_beverage(self):
        c1 = Mocktail('Lemon Punch', '5.9')
        c2 = Mocktail('Tomato Lassi', '6.9')
        c3 = Cocktail('Bloody Mary', '20%', '10.9')
        c4 = Cocktail('Singapore Sling', '30%', '11.9')
        Bar.add_beverage(c1, c2, c3, c4)

    def show_menu(self):
        i = 0
        for b in Bar.beverage:
            i += 1
            print(i, b)

    def order(self):
        while True:
            Bar.show_menu(self)
            print('0 Quit Program')
            user = input('Enter your choice')

            if user == '1':
                c1 = Mocktail('Lemon Punch', '5.9')
                Bar.add_orders(c1)

            if user == '2':
                c2 = Mocktail('Tomato Lassi', '6.9')
                Bar.add_orders(c2)

            if user == '3':
                c3 = Cocktail('Bloody Mary', '20%', '10.9')
                Bar.add_orders(c3)

            if user == '4':
                c4 = Cocktail('Singapore Sling', '30%', '11.9')
                Bar.add_orders(c4)

            if user == '0':
                total = 0
                for b in Bar.orders:
                    print(b)
                    total += float(b.get_price())
                print('The total amount is', round(total, 2))
                break



b = Bar()
b.create_beverage()
b.order()
