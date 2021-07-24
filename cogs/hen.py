import discord
from discord.ext import commands
from discord import embeds, colour
from hentai import *
import random


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
    try:
        title = doujin.json['title']['english']
    except KeyError:
        title = doujin.title()
    embed = embeds.Embed(title=title, url=doujin.url, colour=colour.Colour.blue(), timestamp=ctx.message.created_at)
    embed.set_thumbnail(url=doujin.cover)
    embed.add_field(name="**CODE :**", value=hen_id)
    embed.add_field(name="**Language :**", value=lang, inline=True)
    embed.add_field(name="**Uploaded :**", value=doujin.upload_date.strftime('%d/%m/%Y'))
    embed.add_field(name="**Tags :**", value=tags, inline=True)
    embed.add_field(name="**Characters :**", value=chars, inline=True)
    embed.add_field(name="**Pages :**", value=str(doujin.num_pages))
    embed.add_field(name="**Artist: **", value=author, inline=True)
    embed.set_footer(text=f"Requested by {ctx.author.name}")

    return embed


class Hen(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def hen(self, ctx, *query):
        if len(query) == 0:
            while True:
                hen_id = Utils.get_random_id()
                if Hentai.exists(hen_id):
                    break
            async with ctx.message.channel.typing():
                embed = get_hen_by_id(ctx, hen_id)
            await ctx.send(f'{ctx.author.mention} Here you go, a random hentai!', embed=embed)

        elif len(query) == 1 and str(query[0]).isdigit():
            query = "".join(query)
            hen_id = int(query)
            if Hentai.exists(hen_id):
                async with ctx.message.channel.typing():
                    embed = get_hen_by_id(ctx, hen_id)
                await ctx.send(f'{ctx.author.mention} Here you go, a hentai with code {query}!',
                               embed=embed)
            else:
                await ctx.send(f'{ctx.author.mention} Not found! Check your code again please!')
        else:
            query = " ".join(query)
            list_hen = []
            for hen in Utils.search_by_query(f'{query}', sort=Sort.PopularWeek):
                list_hen.append(hen.id)
            if len(list_hen) != 0:
                hen_id = random.choice(list_hen)
                async with ctx.message.channel.typing():
                    embed = get_hen_by_id(ctx, hen_id)
                await ctx.send(f'{ctx.author.mention} Here you go, search result of "{query}"!',
                               embed=embed)
            else:
                await ctx.send(f'{ctx.author.mention} Not found! Check your name again please!')

    @hen.error
    async def hen_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            ctx.send("Something went wrong! Please try again!")


def setup(client):
    client.add_cog(Hen(client))
