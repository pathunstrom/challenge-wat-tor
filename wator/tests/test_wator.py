import unittest

from wator.wator import Toroid, Position


class TestToroid(unittest.TestCase):

    def setUp(self):
        self.world = Toroid(5, 5)

    def test_up(self):
        self.assertEqual(self.world.up(Position(0, 0)),
                         Position(0, 4))
        self.assertEqual(self.world.up(Position(4, 0)),
                         Position(4, 4))

    def test_left(self):
        self.assertEqual(self.world.left(Position(0, 0)),
                         Position(4, 0))
        self.assertEqual(self.world.left(Position(2, 2)),
                         Position(1, 2))
        self.assertEqual(self.world.left(Position(4, 3)),
                         Position(3, 3))

    def test_right(self):
        self.assertEqual(self.world.right(Position(0, 0)),
                         Position(1, 0))
        self.assertEqual(self.world.right(Position(4, 4)),
                         Position(0, 4))
        self.assertEqual(self.world.right(Position(2, 2)),
                         Position(3, 2))

    def test_down(self):
        self.assertEqual(self.world.down(Position(0, 0)),
                         Position(0, 1))
        self.assertEqual(self.world.down(Position(4, 4)),
                         Position(4, 0))
        self.assertEqual(self.world.down(Position(2, 2)),
                         Position(2, 3))
