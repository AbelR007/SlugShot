import discord
from discord.ext import commands


class Career(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        description = "Progress and Advance in your Career! And gain expierence!",
    )
    async def career(self, ctx):
        embed = discord.Embed(title="Work in Progress",color=ctx.bot.invis)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Career(bot))