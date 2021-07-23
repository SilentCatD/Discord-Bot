import discord
import random
from discord.ext import commands


class Minigame(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'{round(self.client.latency * 1000)}ms')

    @commands.command(aliases=['8ball'])
    async def eight_ball(self, ctx, *, question=""):
        if question == "":
            await ctx.send("Ask me something!")
            return
        answer = ["It is certain.",
                  "It is decidedly so.",
                  "Without a doubt.",
                  "Yes - definitely.",
                  "You may rely on it.",
                  "As I see it, yes.",
                  "Most likely.",
                  "Outlook good.",
                  "Yes.",
                  "Signs point to yes.",
                  "Reply hazy, try again.",
                  "Ask again later.",
                  "Better not tell you now.",
                  "Cannot predict now.",
                  "Concentrate and ask again.",
                  "Don't count on it.",
                  "My reply is no.",
                  "My sources say no.",
                  "Outlook not so good.",
                  "Very doubtful."]
        await ctx.send(f'Question: {question}\nAnswer: {random.choice(answer)}')

    @commands.command()
    async def flip(self, ctx):
        answer = ['Head', 'Tail']
        await ctx.send(f'It\'s {random.choice(answer)}!')

    @commands.command()
    async def say(self, ctx, *, term=""):
        if term == "":
            await ctx.send("Say what?")
            return
        await ctx.send(term)

    @commands.command()
    async def roll(self, ctx, dices: int):
        dices_list = []
        if dices > 9:
            '''
            await ctx.send("Can't roll more than 10 dices")
            return
            '''
            raise ValueError("Can't have more than 10 dice rolled!")
        for _ in range(dices):
            dices_list.append(str(random.randint(1, 6)))
        await ctx.send(f'Result: {" ,".join(dices_list)}')

    @roll.error
    async def roll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Result: {random.randint(1, 6)}')
        if isinstance(error, commands.BadArgument):
            await ctx.send(f'Parameter must be a number!')
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(f'Can\'t roll more than 9 dices at the same time!')


def setup(client):
    client.add_cog(Minigame(client))
