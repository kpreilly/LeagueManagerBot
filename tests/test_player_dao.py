import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.dao.player_dao import get_player, get_players, create_player, update_player, delete_player
from app.models.player import Player
from datetime import datetime, timedelta, timezone

class TestPlayerDAO(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')  # Use an in-memory SQLite database for testing
        self.Session = sessionmaker(bind=self.engine)
        Player.metadata.create_all(self.engine)  # Create Player table
        self.session = self.Session()
        self.player1 = Player(id=1, display_name="Player1", active=True, mmr=1000.0)
        self.player2 = Player(id=2, display_name="Player2", active=False, mmr=2000.0)

    def tearDown(self):
        self.session.query(Player).delete()  # Delete all players after each test
        self.session.commit()

    def test_create_player(self):
        create_player(self.session, self.player1)
        self.assertEqual(get_player(self.session, 1), self.player1)

    def test_get_players(self):
        create_player(self.session, self.player1)
        create_player(self.session, self.player2)
        self.assertEqual(len(get_players(self.session)), 2)

    def test_update_player(self):
        create_player(self.session, self.player1)
        self.player1.active = False
        update_player(self.session, self.player1)
        self.assertEqual(get_player(self.session, 1).active, False)

    def test_delete_player(self):
        create_player(self.session, self.player1)
        delete_player(self.session, 1)
        self.assertEqual(get_player(self.session, 1), None)
    
    def test_created_at(self):
        player = create_player(self.session, self.player1)
        self.assertIsNotNone(player.created_at)
        self.assertIsInstance(player.created_at, datetime)
        now = datetime.now(timezone.utc)
        self.assertTrue(now - timedelta(seconds=5) <= player.created_at.replace(tzinfo=timezone.utc) <= now)

if __name__ == "__main__":
    unittest.main()