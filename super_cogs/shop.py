import autolist
import discord
from discord.ext import commands
# Slash Commands
from discord import Interaction, app_commands
# Database
from exts import items
import consts as c

""" Slash Commands
- /shop
- /buy 
- /sell
- /open
"""

class Shop(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def shopdb(self, user_id):
        shopdb = await self.bot.pg_con.fetchrow("SELECT * FROM shop WHERE userid = $1", user_id)
        if not shopdb:
            await self.bot.pg_con.execute("INSERT INTO shop(userid) VALUES ($1)",user_id)
        shopdb = await self.bot.pg_con.fetchrow("SELECT * FROM shop WHERE userid = $1", user_id)
        return shopdb
    
    async def profiledb(self, user_id):
        profile = await self.bot.pg_con.fetchrow("SELECT * FROM profile WHERE userid = $1", user_id)
        if not profile:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold) VALUES($1, $2)", user_id, 0)
        profile = await self.bot.pg_con.fetchrow("SELECT * FROM profile WHERE userid = $1", user_id)
        return profile
    
    async def error_embed(self, interaction, content, no = 404):
        embed = discord.Embed(
            title=f"Error {no}", description=f"{content}", color=c.error)
        embed.set_footer(text="Any doubts? Join the .support server")
        return await interaction.edit_original_response(embed=embed)

    @app_commands.command(
        description = "Displays the SlugShot Shop"
    )
    async def shop(self, interaction: Interaction):
        
        user_id = int(interaction.user.id)
        shopdb = await self.shopdb(user_id)
        
        embed = discord.Embed(
            title = "Market",
            color = c.main
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/979725346658197524/979726475894849586/1653655381429.png"
        )
        #region Prints the list of items in the Shop
        for name in items:
            cost = items[name][0]
            emoji = items[name][1]
            desc = items[name][2]

            name = name.replace(" ", "_")
            stock = shopdb[name]
            if stock == 0:
                stock = ""
            else:
                stock = f"({stock})"
            name = name.replace("_"," ")

            embed.add_field(
                name = f"{emoji} {name.capitalize()} {stock}",
                value = f"""
                    **Cost** : {cost}{c.gold}
                    **Description** : {desc}
                """,
                inline = False
            )
        #endregion
        await interaction.response.send_message(embed=embed)
        """
        What all does it show?

        - Shop Name
        - Shop Description
        - Shop Items
        """
    
    @app_commands.command(
        description = "Buy an item from the SlugShot Shop"
    )
    @app_commands.rename(
        no = "number"
    )
    @app_commands.describe(
        no = "How many do you want to buy?",
        item = "Which item do you want to buy?"
    )
    async def buy(self, interaction: Interaction, item: str, no: int = 1):
        """Purchase an item from the shop."""

        if no <= 0:
            return await self.error_embed(interaction, "You can't buy 0 or less items.")

        user_id = int(interaction.user.id)
        profiledb = await self.profiledb(user_id)
        shopdb = await self.shopdb(user_id)

        all_items = list(items.keys())
        item = autolist.autocorrect(item, all_items)

        cost = items[item][0] * no
        gold = profiledb['gold']

        if gold < cost:
            return await self.error_embed(interaction, f"Insufficient gold!\nYou need {cost-gold}{c.gold} more gold")

        if item not in items:
            return await self.error_embed(interaction, f"No item called {item} exists!")

        # Embed
        embed = discord.Embed(
            title=f"Are you sure you want to buy {no} {item} for {cost}{c.gold}?",
            color=c.invis
        )
        view = Confirm()
        await interaction.response.send_message(embed=embed, view = view)
        await view.wait()

        if not view.value: # Timed Out
            final_embed = discord.Embed(
                title=f"Timeout!",
                color=c.error
            )
        
        elif view.value: # Confirmed

            gold_left = gold - cost
            item_name_in_db = item.replace(' ', '_')

            await self.bot.pg_con.execute(
                "UPDATE profile SET gold = $1 WHERE userid = $2", gold_left, user_id
            )
            await self.bot.pg_con.execute(
                f"UPDATE shop SET {item_name_in_db} = $1 WHERE userid = $2", shopdb[
                    item_name_in_db] + no, user_id
            )

            final_embed = discord.Embed(
                title=f"Done! You have bought {no} {item} for {cost}{c.gold}!",
                color=c.success
            )

        else: # Cancelled
            final_embed = discord.Embed(
                title="Cancelled!",
                color=c.error
            )
        
        await interaction.edit_original_response(embed=final_embed, view=None)
        """
        What all does it do?

        - Checks if the item exists
        - Checks if the user has enough money
        - Updates the user's money
        - Updates the user's items
        """
    
    @app_commands.command(
        description = "Sell an item from your inventory"
    )
    @app_commands.rename(
        no = "number"
    )
    @app_commands.describe(
        item = "Which item do you want to sell?",
        no = "How many do you want to sell?"
    )
    async def sell(self, interaction: Interaction, item: str, no: int = 1):
        """Sell an item from your inventory."""

        if no <= 0:
            return await self.error_embed(interaction, "You can't sell 0 or less items.")

        user_id = int(interaction.user.id)
        profiledb = await self.profiledb(user_id)
        shopdb = await self.shopdb(user_id)

        all_items = list(items.keys())
        item = autolist.autocorrect(item, all_items)

        cost = items[item][0] * no
        profit = cost - int(cost * (40/100))
        gold = profiledb['gold']

        if item not in items:
            return await self.error_embed(interaction, f"No item called {item} exists!")

        item_name_in_db = item.replace(' ', '_')

        if shopdb[item_name_in_db] < no:
            return await self.error_embed(interaction, f"You don't have {no} {item}!")

        # Embed
        embed = discord.Embed(
            title=f"Are you sure you want to sell {no} {item} for {profit}{c.gold}?",
            color=c.invis
        )
        view = Confirm()
        await interaction.response.send_message(embed=embed, view = view)
        await view.wait()

        if not view.value: # Timed out
            final_embed = discord.Embed(
                title=f"Timeout!",
                color=c.error
            )
        elif view.value: # Confirmed

            gold_left = gold + profit
            item_name_in_db = item.replace(' ', '_')

            await self.bot.pg_con.execute(
                "UPDATE profile SET gold = $1 WHERE userid = $2", gold_left, user_id
            )
            await self.bot.pg_con.execute(
                "UPDATE shop SET {item_name_in_db} = $1 WHERE userid = $2",
                shopdb[item_name_in_db] - no, user_id
            )
            final_embed = discord.Embed(
                title = f"Done! You have sold {no} {item} for {profit}{c.gold}!",
                color = c.success
            )
        
        else: # Cancelled
            final_embed = discord.Embed(
                title="Cancelled!",
                color=c.error
            )

        await interaction.edit_original_response(embed=final_embed, view=None)
        """
        What all does it do?
        
        - Checks if the item exists
        - Checks if the user has enough items
        - Updates the user's money
        - Updates the user's items
        """

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
    await bot.add_cog(Shop(bot))

