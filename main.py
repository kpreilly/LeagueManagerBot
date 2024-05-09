from typing import Final, List, Optional
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, Member, Guild, utils, TextChannel, Object
import asyncio
import re

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
        print('2. Verified: Replace " I " with " | " in display names')
        print('3. Add " | FA" to verified users who have verified role but no FA indicator in their nickname')
        print('4. TEST FEATURE: Get users in voice channels')
        print('Ctrl+C to exit')
        response = input('Choice: ')
        print()
        if response == '1':
            await find_unverified_users_with_rank_check()
        elif response == '2':
            await replace_I_in_verified()
        elif response == '3':
            await add_missing_FA_indicator_to_verified()
        elif response == '4':
            print('Getting users in voice channels\n')

            voice_channels = dict()
            for channel in GUILD.voice_channels:
                voice_channels[channel.name] = channel.members
            for channel, members in voice_channels.items():
                if not members:
                    continue
                print(f'{channel}')
                print(f'\t{', '.join([member.display_name for member in members])}')
            print('\nFinished getting users in voice channels')

        else:
            print('Invalid choice. Please try again.')
        print()

async def add_missing_FA_indicator_to_verified() -> None:
    """Searches for verified users who have the verified role but no FA indicator in their nickname and adds it.
    The FA indicator is " | FA".
    """
    print('Adding " | FA" to verified users who have verified role but no FA indicator in their nickname')
    # get all verified users
    verified_users: List[Member] = await get_all_verified_users()
    # filter out nicknames that already have | [ANYTHING] at the end
    verified_users = [user for user in verified_users if not re.search(r'\| .+$', user.display_name)]
    ignore_list = ['Alfa League', 'zyxi ( ALT )']
    for user in verified_users:
        try:
            if user.display_name in ignore_list:
                continue
            new_display_name: str = user.display_name + ' | FA'
            print(f'Changing {user.display_name} to {new_display_name}')
            await user.edit(nick=new_display_name)
        except Exception as e:
            print(f'Error changing {user.display_name}: {e}')
    print('Finished adding " | FA" to verified users.')

async def replace_I_in_verified() -> None:
    """Searches for verified users who have the verified role and replaces ' I ' with ' | ' in their nickname."""
    print('Cleaning up verified usernames. Changing " I " to " | "')
    # get all verified users
    verified_users: List[Member] = await get_all_verified_users()

    for user in verified_users:
        # check if the user's display name contains ' I '
        if ' I ' in user.display_name:
            # replace ' I ' with ' | '
            new_display_name: str = user.display_name.replace(' I ', ' | ')
            print(f'Changing {user.nick} to {new_display_name}')
            await user.edit(nick=new_display_name)
    print('Finished cleaning up verified usernames.')

async def get_all_unverified_users() -> List[Member]:
    '''Returns a list of GUILD users that have not been verified.'''
    global GUILD
    unverified_users: List[Member] = []
    async for member in GUILD.fetch_members():
        if not any(role.name == 'Verified' for role in member.roles) and not member.bot:
            unverified_users.append(member)
    return unverified_users

async def get_all_verified_users() -> List[Member]:
    '''Returns a list of all users that have been verified.'''
    global GUILD

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
            message.content.startswith('https://rocketleague.tracker.network/rocket-league/profile/')) and \
                message.author in unverified_users:
            result.append(message)
    return result

async def find_unverified_users_with_rank_check() -> None:
    unverified_users: List[Member] = await get_all_unverified_users()
    global GUILD
    print('Scanning the ✅rankcheck✅ channel for /rank commands by unverified users')
    channel: TextChannel = utils.get(GUILD.text_channels, name='✅rankcheck✅')
    if not channel:
        print('Channel ✅rankcheck✅ not found.')
        return
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
