import discord
from discord.ext import commands
from discord import app_commands
import consts as c
from discord import Interaction

""" About SlugShot
- /about
- /invite
- /support
- /ping
"""

class AboutCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(
        name = "about",
        description = "Displays information regarding the SlugShot Bot",
    )
    async def about_command(self, interaction: Interaction) -> None:
        embed = discord.Embed(
            title="About SlugShot",
            description="SlugShot is a fan-created Slugterra-series based Discord Game Bot that provides entertainment to Slugterra fans and everyone in general. Catch, Trade, and Duel Slugs in an ever-updating Bot.",
            colour = c.main
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
        await interaction.response.send_message(embed = embed)
    
    @app_commands.command(
        name = "invite",
        description = "Provides the invite link for the SlugShot bot"
    ) # /invite
    async def invite_command(self, interaction: Interaction) -> None:
        embed = discord.Embed(
            title = "Invite SlugShot",
            description = f"""
                Click the below link to invite the SlugShot Bot
                [Invite As Administrator](https://discord.com/api/oauth2/authorize?client_id=744238855724466238&permissions=8&scope=bot)
                [Invite with Basic Permissions](https://discord.com/api/oauth2/authorize?client_id=744238855724466238&permissions=1256479652928&scope=bot)
            """,
            colour = c.green 
        )
        await interaction.response.send_message(embed = embed)
    
    @app_commands.command(
        name = "support",
        description = "Provides the support server link for the SlugShot bot"
    ) # /support
    async def support_command(self, interaction: Interaction):
        embed = discord.Embed(
            title = "Support SlugShot",
            description= "Join the [Official SlugShot Support Server](https://discord.io/slugshot)\nOR need to suggest anything? use `.support`",
            colour = c.green
        )
        await interaction.response.send_message(embed = embed)
    
    @app_commands.command(
        name = "ping",
        description = "Shows the latency of the bot",
    ) # /ping
    async def ping_command(self, interaction: Interaction):
        user = interaction.user
        embed = discord.Embed(
            description = f"**Pong, {user.mention}!**\nBot Latency: {round(self.bot.latency * 1000)} ms",
            colour = c.green
        )
        await interaction.response.send_message(embed = embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AboutCog(bot))
