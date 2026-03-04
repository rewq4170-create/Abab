import random
import time

class Character:
    def __init__(self, name, health, attack_power):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.is_alive = True

    def attack(self, other):
        if self.is_alive:
            damage = random.randint(0, self.attack_power)
            other.health -= damage
            if other.health <= 0:
                other.is_alive = False
            print(f"{self.name} attacks {other.name} for {damage} damage!")
            print(f"{other.name} has {other.health} health left.")

    def heal(self):
        if self.is_alive:
            heal_amount = random.randint(5, 20)
            self.health += heal_amount
            print(f"{self.name} heals for {heal_amount} health!")

class RPGGame:
    def __init__(self):
        self.characters = []

    def add_character(self, character):
        self.characters.append(character)

    def battle(self):
        while all(c.is_alive for c in self.characters):
            for character in self.characters:
                if character.is_alive:
                    opponent = random.choice([c for c in self.characters if c != character and c.is_alive])
                    action = random.choice(['attack', 'heal'])
                    if action == 'attack':
                        character.attack(opponent)
                    else:
                        character.heal()
                    time.sleep(1)
                    if not opponent.is_alive:
                        print(f"{opponent.name} has been defeated!")
                        break

# Example usage
if __name__ == '__main__':
    game = RPGGame()
    hero = Character('Hero', 100, 20)
    monster = Character('Monster', 50, 15)
    game.add_character(hero)
    game.add_character(monster)
    game.battle()
