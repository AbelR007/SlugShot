import discord
from discord.ext import commands
import consts as c
from discord import app_commands

""" Guide Commands
- /guide
- /help
"""

class DropDown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Battle',description='',emoji='🔫'),
            discord.SelectOption(label='Info',description="",emoji='🔫')
        ]
        super().__init__(
            placeholder = 'Select an option',
            min_values = 1,
            max_values = 1,
            options = options
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(f'You selected {self.values[0]}')

class DropDownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(DropDown())

class Guide(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(
        description = "A Guide for SlugShot Slinger"
    )
    async def g(self, interaction: discord.Interaction) -> None:

        view = DropDownView()

        main_embed = discord.Embed(
            title = "Guide to SlugShot",
            description = f"""
            New Player? `/start`
            More doubts? `/support`
            """,
            color = c.main
        )
        await interaction.response.send_message(embed = main_embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Guide(bot))
