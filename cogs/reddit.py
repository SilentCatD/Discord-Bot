import discord
from discord import Embed
from discord.ext import commands
import praw

reddit = praw.Reddit(
    client_id="HBtFanSntocxgSWJT8KnXA",
    client_secret="rYWaEamC6Y8fZ96WUvuzB0peSZ3CuA",
    user_agent="discord:angry-cat:1.0",
)


class Reddit(commands.Cog):
    def __int__(self, client):
        self.client = client

    @commands.command()
    async def aww(self, ctx):
        submission = None
        async with ctx.message.channel.typing():
            for sub in reddit.subreddit("aww").random_rising(limit=None):
                if sub.url.endswith(('.jpg', '.png', '.gif', '.jpeg')):
                    submission = sub
                    break
            if submission is None:
                await ctx.send("Something went wrong! Try again")
                return
            embed = Embed(title=submission.title,
                          color=discord.Color.blue())
            embed.set_author(name=submission.author.name, icon_url=submission.author.icon_img)
            embed.set_image(url=submission.url)
            embed.set_footer(text=f'{submission.score} likes')
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Reddit(client))
