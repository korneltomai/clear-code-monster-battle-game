from random import randint

class Bleed:
    def __init__(self, target, print_action):
        self.target = target
        self.print_action = print_action
        self.name = "bleed"
        self.duration = 5
        self.remaining_duration = 5
        self.damage = 5

    def apply(self):
        self.target.health -= self.damage
        self.remaining_duration -= 1
        self.print_action(f"{self.target.name} bleeds for 5 damage!")

class Paralysis:
    def __init__(self, target, print_action):
        self.target = target
        self.print_action = print_action
        self.name = "paralysis"
        self.duration = 3
        self.remaining_duration = 3

    def apply(self):
        self.target.stunned = False
        if randint(1, 100) > 50:
            self.target.stunned = True
            self.print_action(f"{self.target.name} cannot move!")
        self.remaining_duration -= 1

class Drain:
    def __init__(self, user, target, print_action):
        self.user = user
        self.target = target
        self.print_action = print_action
        self.name = "drain"
        self.duration = 3
        self.remaining_duration = 3
        self.damage = 5

    def apply(self):
        self.user.health += self.damage
        self.target.health -= self.damage
        self.remaining_duration -= 1
        self.print_action(f"{self.user.name} drains {self.damage} HP from {self.target.name}!")