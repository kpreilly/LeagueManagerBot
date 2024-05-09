import unittest
from unittest.mock import patch, MagicMock, ANY
from app.main import add_verified_users_to_db
from app.models.player import Player
import asyncio
from datetime import datetime, timezone

class TestMain(unittest.TestCase):
    @patch('main.get_all_verified_users')
    @patch('main.player_dao')
    def test_add_verified_users_to_db(self, mock_player_dao, mock_get_all_verified_users):
        # Arrange
        mock_get_all_verified_users.return_value = [
            MagicMock(id=1, display_name='User1'),
            MagicMock(id=2, display_name='User2'),
        ]
        mock_player_dao.get_player.side_effect = [None, None]

        # Act
        asyncio.run(add_verified_users_to_db())

        # Assert
        mock_get_all_verified_users.assert_called_once()
        mock_player_dao.get_player.assert_any_call(ANY, 1)
        mock_player_dao.get_player.assert_any_call(ANY, 2)
        mock_player_dao.create_player.assert_any_call(ANY, Player(id=1, display_name='User1', created_at=datetime.now(timezone.utc)))
        mock_player_dao.create_player.assert_any_call(ANY, Player(id=2, display_name='User2', created_at=datetime.now(timezone.utc)))

if __name__ == '__main__':
    unittest.main()