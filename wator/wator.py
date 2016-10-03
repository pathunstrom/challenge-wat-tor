import logging
import random
from collections import namedtuple

from wator import configuration

Position = namedtuple("Position", ["x", "y"])
Compass = namedtuple("Compass", ["up", "down", "left", "right"])


class CollisionError(Exception):
    pass


class Fish(object):

    def __init__(self, position: Position, environment: 'Toroid'):
        self.position = position
        self.last_position = None
        self.age = 0
        self.environment = environment
        environment[position] = self
        environment.add(self)

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__,
                                   self.position,
                                   self.environment)

    @property
    def maturity(self):
        # Default is two to prevent bugs with spawning with no last position.
        return configuration.maturity.get(self.__class__.__name__, 2)

    def grow(self):
        self.age += 1

    def die(self):
        self.environment[self.position] = None
        self.environment.remove(self)

    def pick_direction(self):
        possible = self.environment.adjacent_spaces(self.position)
        possible = [pos for pos in possible if self.environment.open(pos)]
        return random.choice(possible or [None])

    def move(self, choice):
        self.last_position = self.position
        self.position = choice
        self.environment.update(self)

    def spawn(self):
        if self.age >= self.maturity:
            if self.last_position is not None:
                self.__class__(self.last_position, self.environment)
            self.age = 0

    def update(self):
        choice = self.pick_direction()
        if choice is not None:
            self.move(choice)
        self.grow()
        self.spawn()


class Prey(Fish):

    def eat(self):
        self.die()
        return configuration.energy.get(self.__class__.__name__, 1)


class Predator(Fish):

    def __init__(self, position: Position, environment: 'Toroid'):
        super().__init__(position, environment)
        self.energy = configuration.initial_energy

    def grow(self):
        super().grow()
        self.energy -= 1
        if self.energy <= 0:
            self.die()

    def chomp(self, choice):
        meal = self.environment[choice]  # type: Prey
        self.energy += meal.eat()
        self.move(choice)

    def pick_meal(self) -> Position:
        possible = self.environment.adjacent_spaces(self.position)
        possible = [p for p in possible if self.environment.contains(p, Prey)]
        return random.choice(possible or [None])

    def update(self):
        choice = self.pick_meal()
        if choice is not None:
            self.chomp(choice)
        else:
            choice = self.pick_direction()
            if choice is not None:
                self.move(choice)
        if self.position is None or self.last_position is None:
            message = "Predator %s with last position %s"
            logging.getLogger(__name__).debug(message, self, self.last_position)
        self.spawn()
        self.grow()

    def spawn(self):
        message = "Predator %s spawning with last position %s"
        logging.getLogger(__name__).debug(message,
                                          self,
                                          self.last_position)


class Toroid(object):

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.map = [[None] * width for _ in range(height)]
        self.creatures = set()

    def __getitem__(self, position: Position) -> Fish:
        return self.map[position.y][position.x]

    def __setitem__(self, position: Position, fish: Fish):
        self.map[position.y][position.x] = fish

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__,
                                   self.width,
                                   self.height)

    def adjacent_spaces(self, position: Position) -> Compass:
        """Return array of positions adjacent to position"""
        return Compass(self.up(position),
                       self.down(position),
                       self.left(position),
                       self.right(position))

    def up(self, position: Position) -> Position:
        y = position.y - 1
        y = y if y >= 0 else self.height - 1
        return Position(position.x, y)

    def down(self, position: Position) -> Position:
        y = position.y + 1
        y = y if y < self.height else 0
        return Position(position.x, y)

    def left(self, position: Position) -> Position:
        x = position.x - 1
        x = x if x >= 0 else self.width - 1
        return Position(x, position.y)

    def right(self, position: Position) -> Position:
        x = position.y + 1
        x = x if x < self.width else 0
        return Position(x, position.y)

    def open(self, position: Position) -> bool:
        return self[position] is None

    def contains(self, position: Position, species: type) -> bool:
        return isinstance(self[position], species)

    def update(self, fish: Fish):
        if self.open(fish.position):
            self[fish.position] = fish
            self[fish.last_position] = None
        else:
            message = "%s collided with %s".format(fish, self[fish.position])
            raise CollisionError(message)

    def remove(self, critter: Fish):
        if critter in self.creatures:
            self.creatures.remove(critter)

    def add(self, critter: Fish):
        self.creatures.add(critter)

    def advance(self):
        for critter in list(self.creatures):  # type: Fish
            critter.update()

    def stock(self, amount: int, fish: type):
        for _ in range (amount):
            found = False
            while not found:
                pos = Position(random.randint(0, self.height - 1),
                               random.randint(0, self.width - 1))
                if self.open(pos):
                    found = fish(pos, self)