import discord
import os
import dotenv

dotenv.load_dotenv('.env')
client = discord.Client()


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if client.user == message.author:
        return
    if message.content.startswith('$hello'):
        await message.channel.send("Hello!")


client.run(os.getenv('TOKEN'))
