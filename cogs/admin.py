import json
import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=""):
        await member.kick(reason=reason)
        await ctx.send(f'Kicked {member.mention}')

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("No such member to kick!")

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason=""):
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member.mention}')

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("No such member to ban!")

    @commands.command()
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            if(user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("Can't unban this member! Check their name and try again!")

    @commands.command()
    async def clear(self, ctx, amount=2):
        if amount > 100:
            raise ValueError("Can't delete more than 100 messages at the same time")
        await ctx.channel.purge(limit=amount)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("Can't delete more than 100 messages at the same time!")

    @commands.command()
    async def change_prefix(self, ctx, prefix: str):
        if len(prefix) > 1:
            raise ValueError("Use 1 character to prefix please!")
        with open('./db/prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes[str(ctx.guild.id)] = prefix
        with open('./db/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        await ctx.send(f'Prefix changed to \'{prefix}\'')

    @change_prefix.error
    async def change_prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Change prefix to what?')
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(f'Use 1 character to prefix please!')

def setup(client):
    client.add_cog(Admin(client))
