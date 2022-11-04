import discord
from discord.ext import commands
import consts as c

""" Battle Commands
- /battle
    - /explore
    - /battle bot
"""

class Battle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(
        description = "Understand how SlugShot battle commands work"
    )
    async def battle(self, ctx: commands.Context):
        server = ctx.message.server

        db_server = await self.bot.pg_con.fetchrow("SELECT * FROM server WHERE serverid = $1", server.id)
        prefix = db_server['prefix']

        embed = discord.Embed(
            title = "Battle Commands",
            description = "Battle to improve your slugs and your characters",
            color = c.main
        )
        embed.add_field(
            name = f"{prefix}explore",
            value = "Explore the world to find slugs and items, Battle slugs in the wild with random villagers and npc characters",
            inline = False
        )
        embed.add_field(
            name = f"{prefix}duel @player",
            value = "Challenge another player in a 1v1 slug battle",
            inline = False
        )
        embed.add_field(
            name = f"{prefix}battlebot",
            value = "Battle the Bot for practice to improve strategies and tactics",
            inline = False
        )
        await ctx.send(embed = embed)
    
    @commands.command(
        description = "Explore the caverns beyond the locations",
    )
    async def explore(self, ctx: commands.Context):
        await ctx.send("Command under construction")
    
    @commands.command(
        description = "Battle against Random Characters to develop strategies and tactics",
        aliases = ['botbattle','bb']
    )
    async def battlebot(self, ctx: commands.Context):
        await ctx.send("Command under construction")

async def setup(bot):
    await bot.add_cog(Battle(bot))
