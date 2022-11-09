import discord
from discord.ext import commands
from discord import app_commands, Interaction # Slash
from exts import locations
import consts as c

""" Battle Commands
- /regions
- /mylocation
- /travel <region>
"""

class ExploreCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(
        description = "View all regions"
    )
    async def regions(self, interaction: Interaction):
        user = interaction.user
        db_profile = await self.profiledb(user.id)
        current_region = db_profile['region']
        current_location = db_profile['location']

        embed = discord.Embed(
            # title = "Regions",
            # description = f"**Current Location:** {current_location}",
            color = c.main,
        )
        regions_list = list(locations.keys())
        for i in range(len(regions_list)):
            region_name = regions_list[i]

            locations_text = ""
            for location in locations[regions_list[i]]:
                if location == current_location:
                    locations_text += f"_{location.title()}_\n"
                    continue
                locations_text += f"{location.title()}\n"

            embed.add_field(
                name = f"{region_name}",
                value = f"{locations_text}",
                inline = True
            )
        embed.set_author(
            name = f"Regions",
            icon_url="https://icons.veryicon.com/png/o/object/material-design-icons-1/map-marker-circle.png"
        )
        embed.set_footer(
            text = f"Current Location : {current_location}"
        )
        embed.set_thumbnail(
            url = "https://cdn-icons-png.flaticon.com/512/854/854929.png"
        )
        await interaction.response.send_message(embed = embed)
    
    async def profiledb(self, user_id):
        profile = await self.bot.pg_con.fetchrow("SELECT * FROM profile WHERE userid = $1", int(user_id))
        if not profile:
            await self.bot.pg_con.execute("INSERT INTO profile (userid, gold) VALUES ($1, $2)", int(user_id), 0)
        profile = await self.bot.pg_con.fetchrow("SELECT * FROM profile WHERE userid = $1", int(user_id))
        return profile
    
    @app_commands.command(
        description = "View your current location"
    )
    async def mylocation(self, interaction: Interaction):

        user = interaction.user
        db_profile = await self.profiledb(user.id)

        location = db_profile['location']
        region = db_profile['region']

        embed = discord.Embed(
            title = "Current Location",
            description = f"You are currently at the\n_{location}_, **{region}**",
            color = c.main
        )
        embed.set_thumbnail(
            url = "https://cdn.dribbble.com/users/2837665/screenshots/14717475/2e05aa68-f9e7-4cda-b7e4-7f9f29a208e7_4x.png"
        )
        await interaction.response.send_message(embed=embed)
    
    group = app_commands.Group(
        name = "goto",
        description = "Travel somewhere"
    )

    @group.command(
        description = "Travel to a new location"
    )
    @app_commands.rename(
        loc = "location"
    )
    @app_commands.describe(
        loc = "Which location do you want to travel to?"
    )
    async def location(self, interaction: Interaction, loc: str):
        user = interaction.user
        db_profile = await self.profiledb(user.id)

        location = db_profile['location']
        region = db_profile['region']

        current_gold = db_profile['gold']

        current_loc_no = locations[region][location]
        
        if loc not in locations[region]:
            return await interaction.response.send_message("That location doesn't exist in this region!")
        
        new_loc_no = locations[region][loc]
        cost = (abs(current_loc_no - new_loc_no)) * 50

        if (current_gold - cost) < 0:
            return await interaction.response.send_message("You don't have enough gold to travel there!")

        embed = discord.Embed(
            description = f"Are you sure you want to **travel** to *{loc}* for {cost}{c.gold}?",
            color = c.main
        )
        view = Confirm()
        await interaction.response.send_message(embed = embed, view=view)
        await view.wait()

        if not view.value:  # Timed out
            final_embed = discord.Embed(
                description=f"Timeout!",
                color=c.error
            )
        elif view.value:  # Confirmed
            await self.bot.pg_con.execute(
                "UPDATE profile SET location = $1 WHERE userid = $2", 
                loc, user.id
            )
            await self.bot.pg_con.execute(
                "UPDATE profile SET gold = $1 WHERE userid = $2", 
                current_gold - cost, user.id
            )
            final_embed = discord.Embed(
                description = f"Travelled to {loc}!\n{cost} gold was deducted from your account",
                color=c.success
            )
        
        else:
            final_embed = discord.Embed(
                description=f"Cancelled!",
                color=c.error
            )
        await interaction.edit_original_response(embed = final_embed, view = None)

    @group.command(
        description = "Travel to a new region"
    )
    @app_commands.rename(
        reg = "region"
    )
    @app_commands.describe(
        reg = "Which region do you want to travel to?"
    )
    async def region(self, interaction: Interaction, reg: str):
        embed = discord.Embed(
            title = "Are you sru"
        )
        await interaction.response.send_message(embed)

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 10.0)
        self.value = None

    @discord.ui.button(
        label = "Confirm",
        style = discord.ButtonStyle.green
    )
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.send_message("Confirming...",ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(
        label = "Cancel",
        style = discord.ButtonStyle.red
    )
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.send_message("Cancelling...", ephemeral=True)
        self.value = False
        self.stop()

async def setup(bot: commands.Bot):
    await bot.add_cog(ExploreCog(bot))
