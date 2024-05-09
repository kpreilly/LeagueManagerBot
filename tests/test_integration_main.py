import asyncio
import unittest
from unittest.mock import patch, MagicMock
from discord import Member, Role
from sqlalchemy.exc import SQLAlchemyError

from main import add_verified_users_to_db, get_all_verified_users
from models.player import Player

class AsyncMock(MagicMock):
    async def __aiter__(self):
        return self
    async def __anext__(self):
        try:
            return next(self.it)
        except StopIteration:
            raise StopAsyncIteration
    def setup_async_iter(self, items):
        self.it = iter(items)

class TestIntegrationMain(unittest.TestCase):
    @patch('main.get_all_verified_users')
    @patch('main.GUILD')
    @patch('main.get_db_session')
    @patch('main.player_dao')
    def test_add_verified_users_to_db(self, mock_player_dao, mock_get_db_session, mock_guild, mock_get_all_verified_users):
        # Arrange
        mock_guild.return_value = True
        mock_get_db_session.return_value = MagicMock()
        mock_player_dao.get_player.return_value = None
        mock_player_dao.create_player.return_value = None
    
        verified_user = MagicMock(spec=Member, id=12345678901234567, display_name='User1')
        mock_get_all_verified_users.return_value = [verified_user]
    
        # Act
        asyncio.run(add_verified_users_to_db())
    
        # Assert
        mock_player_dao.get_player.assert_called_once_with(mock_get_db_session.return_value, 12345678901234567)
        mock_player_dao.create_player.assert_called_once_with(
            mock_get_db_session.return_value, Player(id=12345678901234567, display_name='User1'))

    @patch('main.GUILD')
    def test_get_all_verified_users(self, mock_guild):
        # Arrange
        verified_role = MagicMock(spec=Role, name='Verified')
        member = MagicMock(spec=Member, roles=[verified_role], bot=False)
        mock_fetch_members = AsyncMock()
        mock_fetch_members.setup_async_iter([member])
        mock_guild.fetch_members = mock_fetch_members

        # Act
        verified_users = asyncio.run(get_all_verified_users())

        # Assert
        self.assertEqual(verified_users, [member])
