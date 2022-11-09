import discord
from discord.ext import commands
import consts as c
# Slash commands
from discord import app_commands, Interaction

""" Profile Commands
- /profile
- /team [user]
# - /stats
- /wallet [user]
# - /bag
- /share [slinger] [gold]
- /teamswap [pos1] [pos2]
"""

class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        description = "Displays information about the slugs in his team, character and current status"
    )
    async def profile(self, interaction: Interaction):
        await interaction.response.send_message("Work under construction")
        """
        What all does it show?

        - User Name and User ID

        - Current Combined Level [Level of all Characters]
        - Current Combined EXP [EXP of all Characters]

        - Current Character Enabled
        - Current 4 slugs enabled in /team
        - Current Location
        """

    @app_commands.command(
        description = "Displays your arsenal containing slugs and character information"
    )
    @app_commands.describe(
        user = "Check other slinger's arsenal"
    )
    async def team(self, interaction: Interaction, user: discord.Member = None):
        member = user
        if member is None:
            member = interaction.user
        member_name = member.name
        member_id = member.id

        # Getting the Profile USER Database
        db_member = await self.bot.pg_con.fetchrow("SELECT * FROM profile WHERE userid = $1", member_id)

        wins = db_member['wins']
        # print(wins, db_member['wins'])
        loses = db_member['loses']

        main_embed = discord.Embed(
            title = f"Trainer **{member_name}**",
            description = f"Wins = {wins} & Loses = {loses}",
            color = c.main
        )
        for i in range(1,6+1):
            slug = db_member[f'team{i}']
            if not slug:
                slug = "None"
                main_embed.add_field(
                    name = f"No Slug",
                    value = f"\u2800",
                    inline = True
                )
                continue

            # Getting the Slug Database
            db_slug = await self.bot.pg_con.fetchrow("SELECT * from allslugs WHERE slugid = $1", slug)

            slug_name = db_slug['slugname']
            slug_level = db_slug['level']
            slug_rank = db_slug['rank']
            slug_exp = db_slug['exp']

            # For aquiring more specific data, we need SlugData Database
            db_slugdata = await self.bot.pg_con.fetchrow("SELECT * from slugdata WHERE slugname = $1", slug_name)
            slug_emoji = db_slugdata['slugemoji']

            main_embed.add_field(
                name = f"#{i} | {slug_emoji} {slug_name.capitalize()}",
                value = f"""
                    **Level** {slug_level}
                    **Rank** {slug_rank}
                    **Exp** {slug_exp}
                """,
                inline = True
            )
        await interaction.response.send_message(embed = main_embed)

    async def profiledb(self, user_id):
        profile = await self.bot.pg_con.fetchrow("SELECT * FROM profile WHERE userid = $1", user_id)
        if not profile:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold) VALUES($1, $2)", user_id, 0)
        profile = await self.bot.pg_con.fetchrow("SELECT * FROM profile WHERE userid = $1", user_id)
        return profile

    @app_commands.command(
        description = "Shows the amount of in-game currency you currently have"
    )
    @app_commands.describe(
        user = "Check other slinger's wallet"
    )
    async def wallet(self, interaction: Interaction, user: discord.Member = None):
        if not user:
            user = interaction.user
        user_id = user.id

        db_profile = await self.profiledb(user_id)

        gold = db_profile['gold']
        crystals = db_profile['crystal']
        gem = db_profile['gem']

        embed = discord.Embed(
            color = c.main
        )
        embed.add_field(
            name = "Gold",
            value = f"{gold} {c.gold}",
            inline = True
        )
        embed.add_field(
            name = "Crystals",
            value = f"{crystals} {c.crystal}",
            inline = True
        )
        embed.add_field(
            name = "Gems",
            value = f"{gem} {c.gem}",
            inline = True
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/841619355958902814/976436855279058984/1652871075179.png"
        )
        embed.set_author(
            name = f"{user.name}'s Wallet",
            icon_url = user.avatar.url if user.avatar else "https://www.howtogeek.com/wp-content/uploads/2021/07/Discord-Logo-Lede.png?height=200p&trim=2,2,2,2"
        )
        await interaction.response.send_message(embed = embed)

    @app_commands.command(
        description = "Shares coins with the other user"
    )# Share
    @app_commands.rename(
        other = "slinger",
        amount = "gold"
    )
    @app_commands.describe(
        other = "User to share coins with",
        amount = "Amount of coins to share"
    )
    async def share(self, interaction: Interaction, other: discord.Member, amount: int):
        user = interaction.user

        db_user = await self.profiledb(user.id)
        db_other = await self.profiledb(other.id)

        user_gold = db_user['gold']
        other_gold = db_other['gold']

        if amount < 0:
            return await interaction.response.send_message("Negative numbers not allowed")

        elif amount > user_gold:
            return await interaction.response.send_message("You don't have enough gold to share!")

        else:
            pass

        # Confirm Embed
        view = Confirm()
        main_embed = discord.Embed(
            title = f"Are you sure you want to share {amount}{c.gold} to {other}?",
            color = c.invis
        )
        await interaction.response.send_message(embed = main_embed,view = view)
        await view.wait()

        user_ngold = user_gold - amount
        other_ngold = other_gold + amount

        if view.value is None: # Timed Out
            # print("Timed Out.")
            embed = discord.Embed(
                title = f"Timed Out!",
                color = c.invis
            )

        elif view.value: # Confirmed
            # print("Confirmed.")
            await self.bot.pg_con.execute(
                "UPDATE profile SET gold = $1 WHERE userid = $2",
                user_ngold, user.id
            )
            await self.bot.pg_con.execute(
                "UPDATE profile SET gold = $1 WHERE userid = $2",
                other_ngold, other.id
            )

            embed = discord.Embed(
                title = f"Completed!",
                description = f"Shared {amount}{c.gold} to {other}",
                color = c.green
            )

        else: # Cancelled
            # print("Cancelled.")
            embed = discord.Embed(
                title = f"Cancelled!",
                color = c.red
            )

        await interaction.edit_original_response(embed = embed, view = None)
    
    @app_commands.command(
        description = "Swaps the slugs in the team"
    )
    @app_commands.rename(
        pos1 = "position-1", pos2 = "position-2"
    )
    @app_commands.describe(
        pos1 = "Type the position of the slug you want to swap for",
        pos2 = "Type the position of the slug you want to swap with"
    )
    async def swap(self, interaction: Interaction, pos1: int, pos2: int):
        user = interaction.user
        user_id = user.id

        db_profile = await self.profiledb(user_id)

        if (pos1 not in [1,2,3,4]) or (pos2 not in [1,2,3,4]):
            return await interaction.response.send_message("Invalid position")
        
        slug1 = db_profile[f'team{pos1}']
        slug2 = db_profile[f'team{pos2}']

        await self.bot.pg_con.execute(
            "UPDATE profile SET team1 = $1 WHERE userid = $2",
            slug2, user_id
        )
        await self.bot.pg_con.execute(
            "UPDATE profile SET team2 = $1 WHERE userid = $2",
            slug1, user_id
        )
        slug_name1 = (await self.bot.pg_con.fetchrow("SELECT * FROM allslugs WHERE slugid = $1",slug1))['slugname']
        slug_name2 = (await self.bot.pg_con.fetchrow("SELECT * FROM allslugs WHERE slugid = $1",slug2))['slugname']

        embed = discord.Embed(
            title = f"Swapped!",
            description = f"{slug_name1.title()} \U0001f501 {slug_name2.title()}",
            color = c.main
        )
        await interaction.response.send_message(embed = embed)


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
    await bot.add_cog(Profile(bot))
