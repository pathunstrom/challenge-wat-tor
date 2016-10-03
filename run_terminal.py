import logging
import os
from random import choice, randint
from time import sleep

from wator.wator import Fish, Predator, Prey, Toroid, Position


def render(world):
    display = [""] * 20
    for row in world.map:
        sub_display = []
        for space in row:
            if isinstance(space, Predator):
                sub_display.append(choice(["\\", "/"]))
            elif isinstance(space, Prey):
                sub_display.append(choice([">", "<"]))
            else:
                sub_display.append("~")
        display.append(" ".join(sub_display))

    print("\n".join(display))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    wator = Toroid(15, 15)

    wator.stock(2, Prey)
    wator.stock(1, Predator)

    while True:
        render(wator)
        wator.advance()
        sleep(1)
