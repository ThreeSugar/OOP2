import random

class Monster:
    def __init__(self, name, health, attack, defense):
        self.__name = name
        self.__health = health
        self.__attack = attack
        self.__defense = defense

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_health(self):
        return self.__health

    def set_health(self, health):
        self.__health = health

    def get_attack(self):
        return self.__attack

    def set_attack(self, attack):
        self.__attack = attack

    def get_defense(self):
        return self.__defense

    def set_defense(self, defense):
        self.__defense = defense


class FireMonster(Monster):
    def __init__(self):
        super().__init__(name='firebug', health='10', attack='9', defense='4')


class WaterMonster(Monster):
    def __init__(self):
        super().__init__(name='waterbird', health='15', attack='6', defense='3')


class GrassMonster(Monster):
    def __init__(self):
        super().__init__(name='grasshopper', health='20', attack='5', defense='3')


def display_info(monster):
    if isinstance(monster, FireMonster):
        print('{} is a Fire Type monster'.format(FireMonster.get_name(monster)))

    elif isinstance(monster, WaterMonster):
        print('{} is a Water Type monster'.format(WaterMonster.get_name(monster)))

    elif isinstance(monster, GrassMonster):
        print('{} is a Grass Type monster'.format(GrassMonster.get_name(monster)))

    else:
        print('This is not a valid argument.')


# m1 = FireMonster()
# m2 = WaterMonster()
# display_info(m1)
# display_info(m2)


class MonsterGame(FireMonster, WaterMonster, GrassMonster):
    @staticmethod  #callable without instantiating the class first.
    def choose_monster():
        active = True
        while active:
            try:
                choice = input('Choose your monster (F, W or G): ').lower()
                if choice == 'f':
                    player_monster = FireMonster()
                    active = False
                    return player_monster

                elif choice == 'w':
                    player_monster = WaterMonster()
                    active = False
                    return player_monster

                elif choice == 'g':
                    player_monster = GrassMonster()
                    active = False
                    return player_monster

                else:
                    raise ValueError

            except ValueError:
                print('Please select a valid input')

    @staticmethod
    def generate_monster():
        rng = random.randint(1, 3)
        if rng == 1:
            computer_monster = FireMonster()
            return computer_monster
        elif rng == 2:
            computer_monster = WaterMonster()
            return computer_monster
        elif rng == 3:
            computer_monster = GrassMonster()
            return computer_monster

        else:
            print('An unexpected error has occurred!')

    @staticmethod
    def main():
        player = MonsterGame.choose_monster()
        enemy = MonsterGame.generate_monster()

        # ALWAYS PUT THIS KIND OF VARIABLE OUTSIDE OF WHILE LOOP!!!
        # IF YOU PUT THIS KIND OF VARIABLE INSIDE OF WHILE LOOP...
        # IT WILL NEVER DROP TO ZERO!!!
        player_health = int(player.get_health())
        enemy_health = int(enemy.get_health())

        running = True
        while running:
            player_dmg = int(player.get_attack()) - int(enemy.get_defense())
            enemy_health -= player_dmg
            print('{} suffers {} damage, the health is now {}'.format(enemy.get_name(), player_dmg, enemy_health))

            enemy_dmg = int(enemy.get_attack()) - int(player.get_defense())
            player_health -= enemy_dmg
            print('{} suffers {} damage, the health is now {}'.format(player.get_name(), enemy_dmg, player_health))

            if player_health <= 0:
                running = False
                print('You lose!')

            if enemy_health <= 0:
                running = False
                print('You win!')


MonsterGame.main()
