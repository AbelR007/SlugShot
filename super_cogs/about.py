import discord
from discord.ext import commands

""" About SlugShot
- /about
- /invite
- /support
- /ping
"""

class About(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(
        description = "Displays information regarding the SlugShot Bot"
    ) # /about
    async def about(self, ctx: commands.Context):
        embed = discord.Embed(
            title="About SlugShot",
            description="SlugShot is a fan-created Slugterra-series based Discord Game Bot that provides entertainment to Slugterra fans and everyone in general. Catch, Trade, and Duel Slugs in an ever-updating Bot.",
            colour=ctx.bot.main
        )
        embed.add_field(name="Total Servers :", value=f"{len(self.bot.guilds)}",inline=True)
        embed.add_field(name="Total Users :", value=f"{len(self.bot.users)}",inline=True)
        embed.add_field(name="Owner :", value=f"<@636181565621141505>",inline=True)
        embed.add_field(
            name="Affiliation/Policy :",
            value=f"*SlugShot Bot is NOT affiliated with Slugterra, ESI, or WildBrain.*\nSlugShot is a Fan-created Discord Bot based on the Slugterra shows.",
            inline=False,
        )
        embed.add_field(
            name="Media From :",
            value = f"Media files as in the character skins/ slug images are from Fandom Wikipedia",
            inline=False
        )
        await ctx.send(embed=embed)
    
    @commands.command(
        description = "Provides the invite link for the SlugShot bot"
    ) # /invite
    async def invite(self, ctx: commands.Context):
        embed = discord.Embed(
            title = "Invite SlugShot",
            description = f"""
                Click the below link to invite the SlugShot Bot
                [Invite As Administrator](https://discord.com/api/oauth2/authorize?client_id=744238855724466238&permissions=8&scope=bot)
                [Invite with Basic Permissions](https://discord.com/api/oauth2/authorize?client_id=744238855724466238&permissions=1256479652928&scope=bot)
            """,
            colour = ctx.bot.green 
        )
        await ctx.send(embed = embed)
    
    @commands.command(
        description = "Provides the support server link for the SlugShot bot"
    ) # /support
    async def support(self, ctx: commands.Context):
        embed = discord.Embed(
            title = "Support SlugShot",
            description= "Join the [Official SlugShot Support Server](https://discord.io/slugshot)\nOR need to suggest anything? use `.support`",
            colour = ctx.bot.green
        )
        await ctx.send(embed = embed)
    
    @commands.command(
        description = "Shows the latency of the bot",
    ) # /ping
    async def ping(self, ctx: commands.Context):
        embed = discord.Embed(
            title = f"Pong, {ctx.author.name}!",
            description = f"Bot Latency: {round(self.bot.latency * 1000)} ms",
            colour = ctx.bot.green
        )
        embed.set_footer(text = f"Requested by {ctx.author}")
        await ctx.send(embed = embed)
    
async def setup(bot):
    await bot.add_cog(About(bot))
