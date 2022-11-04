import discord
from discord.ext import commands

""" Admin Commands
- /fetch
- /execute
"""

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(
        description = "Fetches the database",
        hidden = True
    )
    async def fetch(self, ctx, *, cmd):
        if int(ctx.message.author.id) != 636181565621141505:
            return await ctx.send("You are not worthy enough to use this command!")
        data = await self.bot.pg_con.fetch(f"{cmd}")
        await ctx.send(data)
    
    @commands.command(
        description = "Executes the database respectively",
        hidden = True
    )
    # @commands.is_owner()
    async def execute(self, ctx, *, cmd):
        if int(ctx.message.author.id) != 636181565621141505:
            return await ctx.send("You are not worthy enough to use this command!")
        await self.bot.pg_con.execute(f"{cmd}")
        await ctx.send("Done.")

async def setup(bot):
    await bot.add_cog(Admin(bot))
