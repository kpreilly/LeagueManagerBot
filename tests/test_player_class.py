import unittest
from app.models.player import Player
from datetime import datetime, timedelta, timezone

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player1 = Player(id=1, display_name="Player1", active=True, mmr=1000.0)
        self.player2 = Player(id=2, display_name="Player2", active=False, mmr=2000.0)

    def test_create_player(self):
        self.assertEqual(self.player1.id, 1)
        self.assertEqual(self.player1.display_name, "Player1")
        self.assertEqual(self.player1.active, True)
        self.assertEqual(self.player1.mmr, 1000.0)

    def test_set_mmr(self):
        self.player1.set_mmr(1500.0)
        self.assertEqual(self.player1.mmr, 1500.0)
        with self.assertRaises(ValueError):
            self.player1.set_mmr(-1000.0)

    def test_magic_methods(self):
        self.assertTrue(self.player1 < self.player2)
        self.assertTrue(self.player2 > self.player1)
        self.assertFalse(self.player1 == self.player2)
        self.assertTrue(self.player1 != self.player2)
        self.assertTrue(self.player1 <= self.player2)
        self.assertTrue(self.player2 >= self.player1)
        self.assertEqual(self.player1['id'], 1)
        self.player1['id'] = 3
        self.assertEqual(self.player1['id'], 3)


if __name__ == "__main__":
    unittest.main()
