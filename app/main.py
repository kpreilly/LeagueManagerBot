from typing import Final, List, Optional
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Member, Guild, utils, TextChannel, Object
import asyncio
from database.db_setup import get_db_session
from models.player import Player
from sqlalchemy.exc import SQLAlchemyError
from database.dao import player_dao

DATABASE_URL: Final[str] = os.getenv('DATABASE_URL', 'sqlite:///league.db')
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN', 'default_token')
GUILD_NAME: Final[str] = 'Alfa League'
GUILD: Optional[Guild] = None

intents: Intents = Intents.default()
intents.members = True
intents.message_content = True
client: Client = Client(intents=intents)

@client.event
async def on_ready() -> None:
    global GUILD
    GUILD = utils.get(client.guilds, name=GUILD_NAME)
    if not GUILD:
        raise ValueError(f'Guild {GUILD_NAME} not found.')
    print(f'{client.user} has connected to Discord!')
    while True:
        response: Optional[str] = None
        # create a menu to select the action
        print('Select an action:')
        print('1. Find unverified users with rank check')
        print('2. TEST FEATURE: Add users with Verified role to the Players table')
        print('Ctrl+C to exit')
        response = input('Choice: ')
        print()
        if response == '1':
            await find_unverified_users_with_rank_check()
        elif response == '2':
            await add_verified_users_to_db()

        else:
            print('Invalid choice. Please try again.')
        print()

async def add_verified_users_to_db() -> None:
    '''Add users with the Verified role to the Players table.'''
    global GUILD
    if not GUILD:
        raise ValueError('Guild not set.')
    # Get a new DB session
    db = get_db_session()

    try:
        # Get all verified users
        verified_users = await get_all_verified_users()

        for user in verified_users:
            player = player_dao.get_player(db, user.id)
            if not player:
                new_player = Player(id=user.id, display_name=user.display_name)
                player_dao.create_player(db, new_player)
    except SQLAlchemyError as e:
        print(f'Error: an error occurred while adding verified users to the Players table: {e}')
    finally:
        db.close()

async def get_all_unverified_users() -> List[Member]:
    '''Returns a list of GUILD users that have not been verified.'''
    global GUILD
    if not GUILD:
        raise ValueError('Guild not set.')
    unverified_users: List[Member] = []
    async for member in GUILD.fetch_members():
        if not any(role.name == 'Verified' for role in member.roles) and not member.bot:
            unverified_users.append(member)
    return unverified_users

async def get_all_verified_users() -> List[Member]:
    '''Returns a list of all users that have been verified.'''
    global GUILD
    if not GUILD:
        raise ValueError('Guild not set.')
    verified_users: List[Member] = []
    async for member in GUILD.fetch_members():
        if any(role.name == 'Verified' for role in member.roles) and not member.bot:
            verified_users.append(member)
    return verified_users

async def get_channel_message_history(channel: TextChannel) -> List[Message]:
    '''Fetches the message history of a channel in batches of 100 messages.'''
    messages: List[Message] = []
    last_message_id = None
    batches_fetched: int = 0
    while True:
        if last_message_id:
            batch = []
            async for message in channel.history(limit=100, before=Object(id=last_message_id)):
                batch.append(message)
        else:
            batch = []
            async for message in channel.history(limit=100):
                batch.append(message)
        if not batch:
            break
        messages.extend(batch)
        last_message_id = batch[-1].id
        print(f'Fetching messages before {last_message_id}. Batch {batches_fetched+1}.')
        batches_fetched += 1
    return messages

async def get_unverified_rank_check_usage(messages: List[Message], unverified_users: List[Member]) -> List[Message]:
    '''Updates the rank check messages to reflect the current unverified users.'''
    result: List[Message] = []
    for message in messages:
        # check if the user has used the /rank command OR if they've provided a URL starting with
        # https://rocketleague.tracker.network/rocket-league/profile/
        if (message.content.startswith('/rank') or
                message.content.startswith('https://rocketleague.tracker.network/rocket-league/profile/')
            ) and message.author in unverified_users:
            result.append(message)
    return result

async def find_unverified_users_with_rank_check() -> None:
    unverified_users: List[Member] = await get_all_unverified_users()
    global GUILD
    if not GUILD:
        raise ValueError('Guild not set.')

    print('Scanning the ✅rankcheck✅ channel for /rank commands by unverified users')
    channel: Optional[TextChannel] = utils.get(GUILD.text_channels, name='✅rankcheck✅')
    if not channel:
        raise ValueError('Channel ✅rankcheck✅ not found.')
    messages: List[Message] = await get_channel_message_history(channel)
    print(f'Found {len(messages)} messages in the ✅rankcheck✅ channel.')
    unverified_rank_check: List[Message] = await get_unverified_rank_check_usage(messages, unverified_users)
    print(f'Found {len(unverified_rank_check)} messages by unverified users in the ✅rankcheck✅ channel.')
    # print the author (using server specific name (display_name)) and message content
    for message in unverified_rank_check:
        print(f'{message.author.display_name}: {message.content}\n message link: {message.jump_url}')

async def main() -> None:
    try:
        await client.start(TOKEN)
    except KeyboardInterrupt:
        await client.close()
    except asyncio.CancelledError:
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        await client.close()
    print("Exiting main")

if __name__ == '__main__':
    asyncio.run(main())
