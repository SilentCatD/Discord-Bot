import discord
from discord.ext import commands
from discord import Embed
import wavelink
import re

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"


class NotInVoiceChannel(commands.CommandError):
    pass

class AlreadyInVoice(commands.CommandError):
    pass

class NotInSameVoice(commands.CommandError):
    pass

class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)
        self.bot.loop.create_task(self.start_node())

    async def start_node(self):
        await self.bot.wait_until_ready()
        print("Starting Music Node...")
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

    @commands.command()
    async def join(self, ctx):
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise NotInVoiceChannel
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if player.is_connected and player.channel_id == channel.id:
            raise AlreadyInVoice
        if player.is_playing:
            await ctx.send(f'Music stopped!')
            await player.set_pause(True)
        await player.connect(channel.id)
        await player.set_pause(False)

    @join.error
    async def join_error(self, ctx, error):
        if isinstance(error, NotInVoiceChannel):
            await ctx.send(f'{ctx.author.mention} Must be in a voice channel to use this command!')
        if isinstance(error, AlreadyInVoice):
            await ctx.send("I'm already in the same voice channel as you dum-dum!")

    @commands.command()
    async def play(self, ctx, *, query: str = ""):
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise NotInVoiceChannel

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected or channel.id != player.channel_id:
            if player.is_playing:
                await player.set_pause(True)
            await player.connect(channel.id)
            await player.set_pause(False)
        query_search = query.strip("<>")
        if not re.match(URL_REGEX, query_search):
            query_search = f'ytsearch:{query_search}'
        tracks = await self.bot.wavelink.get_tracks(query_search)
        if not tracks or not query:
            await ctx.send("Can't find anything to play! Try again!")
            return
        await player.play(tracks[0])

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, NotInVoiceChannel):
            await ctx.send(f'{ctx.author.mention} Must be in a voice channel to use this command!')
        else:
            raise error

    @commands.command()
    async def pause(self, ctx):
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise NotInVoiceChannel
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.send("I'm not even in a voice channel, how can i pause?")
            return
        if player.channel_id != channel.id:
            raise NotInSameVoice
        if player.is_playing:
            if not player.is_paused:
                await player.set_pause(True)
                await ctx.send("There ya go, paused!")
            else:
                await ctx.send("Already paused! Resume playing first")
        else:
            await ctx.send("I'm not playing anything right now tho")

    @pause.error
    async def pause_error(self, ctx, error):
        if isinstance(error, NotInVoiceChannel):
            await ctx.send(f'{ctx.author.mention} Must be in a voice channel to use this command!')
        if isinstance(error, NotInSameVoice):
            await ctx.send("You must be in the same voice channel as me first!")

    @commands.command()
    async def resume(self, ctx):
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise NotInVoiceChannel
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.send("I'm not even in a voice channel, how can i resume?")
            return
        if player.channel_id != channel.id:
            raise NotInSameVoice
        if player.is_playing:
            if player.is_paused:
                await player.set_pause(False)
                await ctx.send("Resumed")
            else:
                await ctx.send("Playing right now...")
        else:
            await ctx.send("I'm not playing anything right now tho")



def setup(bot):
    bot.add_cog(Music(bot))
