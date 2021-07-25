import discord
from discord.ext import commands
from pybooru import Danbooru


class Art(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def art(self, ctx, *, query: str = ""):
        query = query.strip()
        client = Danbooru('danbooru')
        response = ""
        async with ctx.message.channel.typing():
            if query == "":
                post = client.post_list(random=True, limit=1)
                response = post[0]['file_url']
            else:
                query = query.replace(" ", "_")
                post = client.post_list(random=True, limit=1, tags=query)
                if len(post) == 1:
                    response = post[0]['file_url']
                else:
                    response = "Not found! Try something else!"
        await ctx.send(response)

    @art.error
    async def art_error(self, ctx, error):
        ctx.send("Something went wrong! Try again later")


def setup(client):
    client.add_cog(Art(client))
