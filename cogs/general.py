import random
import datetime
import discord
import json
from discord.ext import commands, tasks

activity_pool = [
    discord.Game("Minecraft"),
    discord.Game('League of Legends'),
    discord.Game('Counter-Strike: Global Offensive'),
    discord.Game('Valorant'),
    discord.Game('Call of Duty: Modern Warfare/Warzone'),
    discord.Game('Fortnite'),
    discord.Game('Apex Legends'),
    discord.Game('Rocket League'),
    discord.Game('Battlefield 4'),
    discord.Game('Overwatch'),
    discord.Game('Tom Clancy\'s Rainbow Six: Siege'),
    discord.Activity(type=discord.ActivityType.listening, name="“Guren No Yumiya” By Linked Horizon – Attack On Titan"),
    discord.Activity(type=discord.ActivityType.listening, name="“Unravel” By TK – Tokyo Ghoul"),
    discord.Activity(type=discord.ActivityType.listening,
                     name="“A Cruel Angel’s Thesis” By Yoko Takahashi – Neon Genesis Evangelion"),
    discord.Activity(type=discord.ActivityType.listening, name="“The Hero” By JAM Project – One Punch Man"),
    discord.Activity(type=discord.ActivityType.listening, name="“The Day” By Porno Graffiti - My Hero Academia"),
    discord.Activity(type=discord.ActivityType.watching, name="Harry Potter and the Goblet of Fire"),
    discord.Activity(type=discord.ActivityType.watching, name="Star Wars: The Rise Of Skywalker"),
    discord.Activity(type=discord.ActivityType.watching, name="The Mummy"),
    discord.Activity(type=discord.ActivityType.watching, name="Lord Of The Ring"),
    discord.Activity(type=discord.ActivityType.watching, name="The Hobbit")
]

response_pool_when_mention = ['Sup?', 'What?', 'How ya doing?', 'What do ya want?',
                              'Err...', 'And...?', 'Ya called?,' 'What do ya need?',
                              'What can i help ya with?',
                              'That\'s me!', 'It\'s a me! Angry-Cat',
                              'Weirdo', 'I\'m here!']


def time_in_range(start, end, x):
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


class General(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.activity = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        mention = f'<@!{self.client.user.id}>'
        if message.content == mention:
            await message.channel.send(f'{random.choice(response_pool_when_mention)}')

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.client.user} is ready!')
        self.change_activity.start()
        self.change_status.start()

    #@commands.Cog.listener()
    #async def on_command_error(self, ctx, error):
        #if isinstance(error, commands.CommandNotFound):
            #await ctx.send("No such command!")
        #else:
            #print(error)

    @tasks.loop(minutes=60)
    async def change_activity(self):
        self.activity = random.randint(0, len(activity_pool) - 1)
        await self.client.change_presence(activity=activity_pool[self.activity])

    @tasks.loop(minutes=1)
    async def change_status(self):
        start = datetime.time(22, 0, 0)
        end = datetime.time(6, 0, 0)
        now = datetime.datetime.now().time()
        if time_in_range(start, end, now):
            await self.client.change_presence(status=discord.Status.idle, activity=activity_pool[self.activity])
        else:
            await self.client.change_presence(status=discord.Status.online, activity=activity_pool[self.activity])

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        default_pre = '!'
        print(f'Joining guild \'{guild.id}\'...')
        with open('./db/prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes[str(guild.id)] = default_pre
        with open('./db/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        print(f'Set default prefixes as \'{default_pre}\'')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(f'Leaving guild \'{guild.id}\'...')
        with open('./db/prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes.pop(str(guild.id))
        with open('./db/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        print(f'Guild\'s prefix deleted')


def setup(client):
    client.add_cog(General(client))
