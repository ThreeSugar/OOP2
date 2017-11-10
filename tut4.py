class Vehicle:
    bicycle_count = 0
    skateboard_count = 0


class Bicycle(Vehicle):

    def __init__(self, gear_count=1):
        Vehicle.bicycle_count += 1
        self.gear_count = gear_count
        self.reg = 'BY' + str(Vehicle.bicycle_count)

    def __str__(self):
        return 'Registration Number: ' + self.reg + ' Gear Count: ' + str(self.gear_count)


class Skateboard(Vehicle):

    def __init__(self, length):
        Vehicle.skateboard_count += 1
        self.length = length
        self.reg = 'SK' + str(Vehicle.skateboard_count)

    def __str__(self):
        return 'Registration Number: ' + self.reg + ' Length: ' + str(self.length)


mountainBike = Bicycle(2)
roadBike = Bicycle()
rollerskate = Skateboard(1)
b = Bicycle(30)

print(mountainBike)
print(roadBike)
print(rollerskate)
print(b)
