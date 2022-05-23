import discord
from discord.ext import commands

class Containers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def container(self, ctx):
        await ctx.send("container")

def setup(bot):
    bot.add_cog(Containers(bot))