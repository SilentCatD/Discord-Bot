from discord.ext import commands
from discord import embeds, colour
import dotenv
import random
from hentai import *

dotenv.load_dotenv('.env')
TOKEN = os.getenv('TOKEN')
bot = commands.Bot(command_prefix="!")


def get_hen_by_id(ctx, hen_id):
    doujin = Hentai(hen_id)
    hen_id = str(hen_id)
    hen_id = hen_id.zfill(6)
    tags = "Not found"
    lang = "Not found"
    author = "Not found"
    chars = "Not found"
    if len(doujin.tag) != 0:
        temp = [_.name for _ in doujin.tag]
        tags = ", ".join(temp)
    if len(doujin.language) != 0:
        lang = doujin.language[0].name
    if len(doujin.artist) != 0:
        author = doujin.artist[0].name
    if len(doujin.character) != 0:
        temp = []
        for _ in doujin.character:
            temp.append(_.name)
        chars = " ,".join(temp)
    embed = embeds.Embed(title=doujin.title(Format.Pretty), url=doujin.url, colour=colour.Colour.blue())
    embed.set_thumbnail(url=doujin.cover)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(name="**Language :**", value=lang, inline=False)
    embed.add_field(name="**Tags :**", value=tags, inline=False)
    embed.add_field(name="**Characters :**", value=chars, inline=False)
    embed.add_field(name="**Artist: **", value=author, inline=False)
    embed.set_footer(text=f'nHentai code is: {hen_id}')
    return embed


@bot.command(name='hen')
async def get_hen(ctx, *query):
    if len(query) == 0:
        while True:
            hen_id = Utils.get_random_id()
            if Hentai.exists(hen_id):
                break
        await ctx.send(f'{ctx.author.mention} Here you go, a random hentai!', embed=get_hen_by_id(ctx, hen_id))

    elif len(query) == 1 and str(query[0]).isdigit():
        query = "".join(query)
        hen_id = int(query)
        if Hentai.exists(hen_id):
            await ctx.send(f'{ctx.author.mention} Here you go, a hentai with code {query}!', embed=get_hen_by_id(ctx, hen_id))
        else:
            await ctx.send(f'{ctx.author.mention} Not found! Check your code again please!')
    else:
        query = " ".join(query)
        print(query)
        list_hen = []
        for hen in Utils.search_by_query(f'{query}', sort=Sort.PopularWeek):
            list_hen.append(hen.id)
        if len(list_hen) != 0:
            hen_id = random.choice(list_hen)
            await ctx.send(f'{ctx.author.mention} Here you go, search result of "{query}"!', embed=get_hen_by_id(ctx, hen_id))
        else:
            await ctx.send(f'{ctx.author.mention} Not found! Check your name again please!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f'{ctx.author.mention} No such command!')
"""
@bot.command(name='play')
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@bot.command(name='leave')
async def leave(ctx):
    await ctx.voice_client.disconnect()
"""

bot.run(TOKEN)
