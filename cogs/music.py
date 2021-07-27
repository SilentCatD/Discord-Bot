import datetime
from discord import Embed
import discord
from discord.ext import commands
import re
import asyncio
import wavelink

YOUTUBE_URL = r"^(http(s)??\:\/\/)?(www\.)?((youtube\.com\/watch\?v=)|(youtu.be\/))([a-zA-Z0-9\-_])+"

OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}


async def millis_to_time(millis):
    seconds = (millis / 1000) % 60
    seconds = int(seconds)
    minutes = (millis / (1000 * 60)) % 60
    minutes = int(minutes)
    hours = (millis / (1000 * 60 * 60)) % 24
    hours = int(hours)

    hours_str = str(hours).zfill(2)
    minutes_str = str(minutes).zfill(2)
    seconds_str = str(seconds).zfill(2)
    if hours > 0:
        return f'{hours_str}:{minutes_str}:{seconds_str}'
    return f'{minutes_str}:{seconds_str}'


class UserNotInVoiceChannel(commands.CommandError):
    pass


class NoQuerySpecified(commands.CommandError):
    pass


class NoResultFound(commands.CommandError):
    pass


class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)
        self.bot.loop.create_task(self.start_node())

    async def cog_check(self, ctx):
        if not ctx.author.voice:
            ctx.send("Ya must be in voice channel to use this command!")
            raise UserNotInVoiceChannel
        return True

    async def start_node(self):
        print("Starting Music Node...")
        await self.bot.wait_until_ready()
        nodes = {
            "Music Bot": {
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "youshallnotpass",
                "identifier": "Music Bot",
                "region": "hong_kong",
            }
        }

        for node in nodes.values():
            await self.bot.wavelink.initiate_node(**node)

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node: wavelink.Node):
        print(f'Node {node.identifier} is ready!')

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node: wavelink.Node):
        print(f'Wavelink node {node.identifier} ready')

    async def choose_song(self, ctx, search_query, tracks):
        async with ctx.typing():
            embed = Embed(title="Choose a song: ",
                          timestamp=datetime.datetime.utcnow())
            embed.set_author(name=f"Search result of '{search_query}'")
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            text = ""
            for index, track in enumerate(tracks):
                if index >= 5:
                    break
                option = list(OPTIONS.keys())[list(OPTIONS.values()).index(index)]
                track = track.info
                length = await millis_to_time(track['length'])
                text += f'{option} [{track["title"]} [{length}] - By {track["author"]}]({track["uri"]})\n\n'
            embed.description = text
        choose = await ctx.send(embed=embed)
        if index == 5:
            index -= 1
        for i in range(index + 1):
            option = list(OPTIONS.keys())[list(OPTIONS.values()).index(i)]
            await choose.add_reaction(option)

        def check(r, u):
            return r.emoji in OPTIONS.keys() and u == ctx.author and choose.id == r.message.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await choose.delete()
            return None
        else:
            song_index = OPTIONS[reaction.emoji]
            await choose.delete()
            await ctx.message.delete()
            return song_index

    async def song_added_embed(self, ctx, track):
        length = await millis_to_time(track['length'])
        text = f'[{track["title"]} [{length}] - By {track["author"]}]({track["uri"]})\n\n'
        embed = Embed(title="New song added", description=text, timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        return embed

    @commands.command()
    async def play(self, ctx, *, query: str = ""):
        url = True
        search_query = query
        query = query.strip("<>")
        if not query:
            raise NoQuerySpecified
        if not re.match(YOUTUBE_URL, query):
            url = False
            query = f'ytsearch:{query}'
        tracks = await self.bot.wavelink.get_tracks(query)
        if not tracks:
            raise NoResultFound
        if url:
            if isinstance(tracks, wavelink.TrackPlaylist):
                print(tracks.tracks)
                print("This is a playlist")
            else:
                async with ctx.typing():
                    # Enqueue here
                    embed = await self.song_added_embed(ctx, tracks[0].info)
                await ctx.message.delete()
                await ctx.send(embed=embed)
                print("This is a single song")
                # add to queue
        else:
            song_index = await self.choose_song(ctx, search_query, tracks)
            async with ctx.typing():
                if song_index is not None:
                    track = tracks[song_index].info
                    embed = await self.song_added_embed(ctx, track)
                    # Enqueue here
            if song_index is not None:
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Not chose anything from search result of '{search_query}'")


def setup(bot):
    bot.add_cog(Music(bot))
