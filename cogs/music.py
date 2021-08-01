import datetime
from discord import Embed
from discord.ext import commands
import re
import asyncio
import wavelink
from typing import Union

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


class BotNotInVoiceChannel(commands.CommandError):
    pass


class NotInSameVoiceChannel(commands.CommandError):
    pass


class AlreadyInSameVoiceChannel(commands.CommandError):
    pass


class NotPlayingAnything(commands.CommandError):
    pass


class AlreadyPlaying(commands.CommandError):
    pass


class AlreadyPaused(commands.CommandError):
    pass


class UserNotInVoiceChannel(commands.CommandError):
    pass


class NoQuerySpecified(commands.CommandError):
    pass


class NoResultFound(commands.CommandError):
    pass


class MusicController:
    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild_id = guild_id
        self.play_next_song = asyncio.Event()
        self.song_queue = asyncio.Queue()
        self.now_playing_message = None
        self.task = self.bot.loop.create_task(self.controller_loop())
        self.channel = None
        self.volume = 40

    async def controller_loop(self):
        await self.bot.wait_until_ready()
        player = self.bot.wavelink.get_player(self.guild_id)
        await player.set_volume(self.volume)
        while True:
            try:
                if self.now_playing_message:
                    await self.now_playing_message.delete()
                self.play_next_song.clear()
                song = await self.song_queue.get()
                await player.play(song)
                track = song.info
                if track["isStream"]:
                    length = "STREAMING"
                else:
                    length = await millis_to_time(track['length'])
                text = f'[{track["title"]} [{length}] - By {track["author"]}]({track["uri"]})\n\n'
                embed = Embed(title="Now playing", description=text)
                embed.set_image(url=song.thumb)
                if self.song_queue._queue:
                    track = self.song_queue._queue[0].info
                    text = f'Up next: {track["title"]} - By {track["author"]}\n\n'
                    embed.set_footer(text=text)
                self.now_playing_message = await self.channel.send(embed=embed)

                await self.play_next_song.wait()
            except asyncio.CancelledError:
                break


class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.bot = bot
        self.controllers = {}
        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)
        self.bot.loop.create_task(self.start_node())

    async def start_node(self):
        print("Starting Music Node...")
        await self.bot.wait_until_ready()

        node = await self.bot.wavelink.initiate_node(host='127.0.0.1',
                                                     port=2333,
                                                     rest_uri='http://127.0.0.1:2333',
                                                     password='youshallnotpass',
                                                     identifier='Music Bot',
                                                     region='hong_kong')

        node.set_hook(self.on_event_hook)

    def get_controller(self, value: Union[commands.Context, wavelink.Player]):
        if isinstance(value, commands.Context):
            guild_id = value.guild.id
        else:
            guild_id = value.guild_id

        try:
            controller = self.controllers[guild_id]
        except KeyError:
            controller = MusicController(self.bot, guild_id)
            self.controllers[guild_id] = controller

        return controller

    async def on_event_hook(self, event):
        if isinstance(event, (wavelink.TrackEnd, wavelink.TrackException)):
            if event.player.guild_id not in self.controllers.keys():
                return
            controller = self.get_controller(event.player)
            controller.play_next_song.set()

    async def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage
        if not ctx.author.voice:
            raise UserNotInVoiceChannel
        return True

    async def cog_command_error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            return await ctx.send('This command can not be used in Private Messages.')
        if isinstance(error, UserNotInVoiceChannel):
            return await ctx.send("Ya must be in voice channel to use this command!")
        if isinstance(error, AlreadyInSameVoiceChannel):
            return await ctx.send('We already in same voice ya dum-dum')
        if isinstance(error, NotPlayingAnything):
            return await ctx.send("But i'm not playing anything right now tho")
        if isinstance(error, AlreadyPaused):
            return await ctx.send("I'm already paused!")
        if isinstance(error, AlreadyPlaying):
            return await ctx.send("I'm already playing...")
        if isinstance(error, BotNotInVoiceChannel):
            return await ctx.send("I'm not in voice channel!")
        if isinstance(error, NotInSameVoiceChannel):
            return await ctx.send("We must be in same voice channel to use this command!")
        if isinstance(error, NoResultFound):
            return await ctx.send("No result found!")
        else:
            raise error

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
                if track["isStream"]:
                    length = "STREAMING"
                else:
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
            return song_index

    async def song_added_embed(self, ctx, track_raw):
        track = track_raw.info
        if track["isStream"]:
            length = "STREAMING"
        else:
            length = await millis_to_time(track['length'])
        text = f'[{track["title"]} [{length}] - By {track["author"]}]({track["uri"]})\n\n'
        embed = Embed(title="New song added", description=text, timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=f"{track_raw.thumb}")
        return embed

    @commands.command()
    async def join(self, ctx):
        user_pause = False
        channel = ctx.author.voice.channel
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)
        controller.channel = ctx.channel
        if channel.id == player.channel_id:
            raise AlreadyInSameVoiceChannel
        if player.current and player.is_paused and player.is_connected:
            user_pause = True
        if not player.is_paused:
            await player.set_pause(True)
        await player.connect(channel.id)
        await ctx.send(f'Connected to {channel.name}')
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if player.current and not user_pause:
            await ctx.send("Song currently playing! Use !resume to continue playing!")

    @commands.command()
    async def play(self, ctx, option: str = "", *, query: str = ""):
        mode = ['-s']
        if option not in mode:
            query = f'{option} {query}'
        url = True
        search_query = query
        query = query.strip()
        if not query:
            raise NoQuerySpecified
        if not re.match(YOUTUBE_URL, query):
            url = False
            query = f'ytsearch:{query}'
        tracks = await self.bot.wavelink.get_tracks(query)
        if not tracks:
            raise NoResultFound
        await ctx.message.delete()
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected or player.channel_id != ctx.author.voice.channel.id:
            await ctx.invoke(self.join)
        controller = self.get_controller(ctx)
        if url:
            if isinstance(tracks, wavelink.TrackPlaylist):
                print(tracks.tracks)
                ctx.send("playlist not supported yet")
            else:
                async with ctx.typing():
                    embed = await self.song_added_embed(ctx, tracks[0])
                    await controller.song_queue.put(tracks[0])
                await ctx.send(embed=embed)
        else:
            if option == '-s':
                song_index = await self.choose_song(ctx, search_query, tracks)
            else:
                song_index = 0
            async with ctx.typing():
                if song_index is not None:
                    embed = await self.song_added_embed(ctx, tracks[song_index])
                    await controller.song_queue.put(tracks[song_index])
            if song_index is not None:
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Not chose anything from search result of '{search_query}'")

    @commands.command()
    async def pause(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            raise BotNotInVoiceChannel
        if not player.current:
            raise NotPlayingAnything
        if player.paused and player.current:
            raise AlreadyPaused
        if player.channel_id != ctx.author.voice.channel.id:
            raise NotInSameVoiceChannel
        await player.set_pause(True)
        await ctx.send('Song paused!')

    @commands.command()
    async def resume(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            raise BotNotInVoiceChannel
        if player.channel_id != ctx.author.voice.channel.id:
            raise NotInSameVoiceChannel
        if not player.is_paused and player.current:
            raise AlreadyPlaying
        if not player.current:
            raise NotPlayingAnything
        if player.is_paused:
            await player.set_pause(False)
        await ctx.invoke(self.now_playing)

    @commands.command()
    async def skip(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            raise BotNotInVoiceChannel
        if player.channel_id != ctx.author.voice.channel.id:
            raise NotInSameVoiceChannel
        if not player.current:
            raise NotPlayingAnything
        await player.stop()
        await ctx.send("Song skipped!")

    @commands.command()
    async def stop(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            raise BotNotInVoiceChannel
        if player.channel_id != ctx.author.voice.channel.id:
            raise NotInSameVoiceChannel
        controller = self.get_controller(ctx)
        try:
            del self.controllers[ctx.guild.id]
            controller.task.cancel()
            await player.stop()
        except KeyError:
            pass
        if not player.is_connected:
            raise NotPlayingAnything
        await player.disconnect()
        await ctx.send("Disconnected")

    @commands.command()
    async def leave(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            raise BotNotInVoiceChannel
        if player.channel_id != ctx.author.voice.channel.id:
            raise NotInSameVoiceChannel
        await player.set_pause(True)
        await ctx.send(f'Music paused!')
        await player.disconnect()

    @commands.command()
    async def now_playing(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            raise BotNotInVoiceChannel
        if player.channel_id != ctx.author.voice.channel.id:
            raise NotInSameVoiceChannel
        if not player.current:
            raise NotPlayingAnything
        controller = self.get_controller(ctx)
        await controller.now_playing_message.delete()
        track = player.current.info
        if track["isStream"]:
            length = "STREAMING"
        else:
            length = await millis_to_time(track['length'])
        text = f'[{track["title"]} [{length}] - By {track["author"]}]({track["uri"]})\n\n'
        embed = Embed(title="Now playing", description=text)
        embed.set_image(url=player.current.thumb)
        if controller.song_queue._queue:
            track = controller.song_queue._queue[0].info
            text = f'Up next: {track["title"]} - By {track["author"]}\n\n'
            embed.set_footer(text=text)
        controller.now_playing_message = await ctx.send(embed=embed)

    @commands.command()
    async def queue(self, ctx):
        """Retrieve information on the next 5 songs from the queue."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            raise BotNotInVoiceChannel
        if player.channel_id != ctx.author.voice.channel.id:
            raise NotInSameVoiceChannel
        controller = self.get_controller(ctx)
        queue_size = controller.song_queue.qsize()
        tracks = []
        for i in range(queue_size):
            tracks.append(controller.song_queue._queue[i])

        async with ctx.typing():
            embed = Embed(title="Now playing: ")
            if len(tracks) - 5 > 0:
                text = f'And {len(tracks) - 5} more songs...'
                embed.set_footer(text=text)
            if not player.current:
                embed.description = "Not playing anything"
            else:
                track = player.current.info
                if track["isStream"]:
                    length = "STREAMING"
                else:
                    length = await millis_to_time(track['length'])
                embed.description = f'[{track["title"]} [{length}] - By {track["author"]}]({track["uri"]})\n\n'
                embed.set_thumbnail(url=player.current.thumb)

            text = ""
            for track in tracks:
                track = track.info
                if track["isStream"]:
                    length = "STREAMING"
                else:
                    length = await millis_to_time(track['length'])
                text += f'[{track["title"]} [{length}] - By {track["author"]}]({track["uri"]})\n\n'
            if not controller.song_queue._queue:
                text = "No upcoming songs"
            embed.add_field(name="Upcoming: ", value=text)
        await ctx.send(embed=embed)





def setup(bot):
    bot.add_cog(Music(bot))
