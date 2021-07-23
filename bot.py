import os
import dotenv
import discord
from discord.ext import commands

dotenv.load_dotenv('.env')
TOKEN = os.getenv('TOKEN')
client = commands.Bot(command_prefix='!')


@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} loaded!')


@load.error
async def load_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send('Unable to load cogs! Maybe it does not exist?')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} unloaded!')


@unload.error
async def unload_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send('Unable to unload cogs! Maybe it does not exist?')


@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} reloaded!')


@reload.error
async def reload_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send('Unable to reload cogs! Maybe it does not exist?')


@client.command()
async def reload_all(ctx):
    for _filename in os.listdir('./cogs'):
        if _filename.endswith('.py'):
            client.unload_extension(f'cogs.{_filename[:-3]}')
            client.load_extension(f'cogs.{_filename[:-3]}')
            await ctx.send(f'{_filename[:-3]} reloaded!')


@reload_all.error
async def reload_all_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send('Unable to reload all cogs! Maybe some cog does not exist?')


def setup():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            print(f'{filename[:-3]} loaded!')


setup()
client.run(TOKEN)
