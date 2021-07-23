import random
import datetime
import discord
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
    discord.Activity(type=discord.ActivityType.listening, name="“A Cruel Angel’s Thesis” By Yoko Takahashi – Neon Genesis Evangelion"),
    discord.Activity(type=discord.ActivityType.listening, name="“The Hero” By JAM Project – One Punch Man"),
    discord.Activity(type=discord.ActivityType.listening, name="“The Day” By Porno Graffiti - My Hero Academia"),
    discord.Activity(type=discord.ActivityType.watching, name="Harry Potter and the Goblet of Fire"),
    discord.Activity(type=discord.ActivityType.watching, name="Star Wars: The Rise Of Skywalker"),
    discord.Activity(type=discord.ActivityType.watching, name="The Mummy"),
    discord.Activity(type=discord.ActivityType.watching, name="Lord Of The Ring"),
    discord.Activity(type=discord.ActivityType.watching, name="The Hobbit")
]


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
    async def on_ready(self):
        print(f'{self.client.user} is ready!')
        self.change_activity.start()
        self.change_status.start()

    #@commands.Cog.listener()
    #async def on_command_error(self, ctx, error):
    #    if isinstance(error, commands.CommandNotFound):
    #        await ctx.send("No such command!")

    @tasks.loop(minutes=60)
    async def change_activity(self):
        self.activity = random.randint(0, len(activity_pool)-1)
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


def setup(client):
    client.add_cog(General(client))
