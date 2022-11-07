import discord
from discord.ext import commands
import consts as c
from .dex import types
from .profile import Profile
# Slash Commands
from discord import Interaction, app_commands

""" Info Commands
- /sluginfo
- /info char
- /upgrade 
"""

class SlugInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def profiledb(self, user_id):
        profile = await self.bot.pg_con.fetchrow("SELECT * FROM profile WHERE userid = $1", user_id)
        if not profile:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold) VALUES($1, $2)", user_id, 0)
        profile = await self.bot.pg_con.fetchrow("SELECT * FROM profile WHERE userid = $1", user_id)
        return profile
    
    @app_commands.command(
        description = "Information about SlugShot dynamics",
    )
    async def info(self, interaction: Interaction, topic: str = None):
        embed = discord.Embed(
            title = "Info Commands",
            color = c.invis
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(
        description = "Gets information about the slug from the team"
    )
    @app_commands.rename(
        pos = "team-position"
    )
    @app_commands.describe(
        pos = "Specify the slug's position in the team"
    )
    async def sluginfo(self, interaction: Interaction, pos: int = 1):
        user = interaction.user
        
        if pos not in [1,2,3,4]:
            return await interaction.response.send_message("Invalid Slug Position")

        db_profile = await self.profiledb(user.id)
        slug_id = db_profile[f'team{pos}']

        if slug_id is None or slug_id == '':
            return await interaction.response.send_message("No slug at that position.")

        # All Slugs DataBase
        db_allslugs = await self.bot.pg_con.fetchrow("SELECT * FROM allslugs WHERE slugid = $1",slug_id)
        user_id = int(db_allslugs['userid'])
        # print(user_id)
        slinger  = self.bot.get_user(user_id)
        # print(slinger)
        
        slug_name = db_allslugs['slugname']
        level = db_allslugs['level']
        rank = db_allslugs['rank']
        exp = db_allslugs['exp']

        iv_health = db_allslugs['iv_health']
        iv_attack = db_allslugs['iv_attack']
        iv_defense = db_allslugs['iv_defense']
        iv_speed = db_allslugs['iv_speed']
        iv_accuracy = db_allslugs['iv_accuracy']
        iv_retrieval = db_allslugs['iv_retrieval']

        ev_health = db_allslugs['ev_health']
        ev_attack = db_allslugs['ev_attack']
        ev_defense = db_allslugs['ev_defense']
        ev_speed = db_allslugs['ev_speed']
        ev_accuracy = db_allslugs['ev_accuracy']
        ev_retrieval = db_allslugs['ev_retrieval']

        item = db_allslugs['item']
        if item == '' or item is None:
            item = "None"
        else:
            item = item.replace("_"," ").capitalize()

        abilityno = db_allslugs['abilityno']
        if abilityno == 1:
            ability = "Base Ability"
        else:
            abilitydb = await self.bot.pg_con.fetchrow(
                "SELECT * FROM ability WHERE slugname = $1 AND abilityno = $2",
                slug_name, abilityno
            )
            ability = abilitydb['ability']
        
        # Slug Stats from FIXED Database
        db_slugdata = await self.bot.pg_con.fetchrow("SELECT * FROM slugdata WHERE slugname = $1", slug_name)

        slug_type = db_slugdata['type']

        health = db_slugdata['health']
        attack = db_slugdata['attack']
        defense = db_slugdata['defense']
        speed = db_slugdata['speed']
        accuracy = db_slugdata['accuracy']
        retrieval = db_slugdata['retrieval']
        imgurl = db_slugdata['protoimgurl']

        type_emoji, embed_clr = types(slug_type)

        # EMBED
        embed = discord.Embed(
            color = embed_clr
        )
        embed.set_author(
            name = f"{slug_name.capitalize()}",
            icon_url = imgurl
        )
        embed.add_field(name="Team Position",value=f"#{pos}",inline=True)
        embed.add_field(name="Level", value=f"{level}", inline=True)
        embed.add_field(name="Experience", value=f"Rank {rank} [{exp}]", inline=True)
        embed.add_field(
            name="Base",
            value=f"""
            **Health**: {health}
            **Attack**: {attack}
            **Defense**: {defense}
            **Speed**: {speed}
            **Accuracy**: {accuracy}
            **Retrieval**: {retrieval}
            """,
            inline=True
        )
        embed.add_field(
            name="IVs",
            value=f"""
            **Health**: {iv_health}
            **Attack**: {iv_attack}
            **Defense**: {iv_defense}
            **Speed**: {iv_speed}
            **Accuracy**: {iv_accuracy}
            **Retrieval**: {iv_retrieval}
            """,
            inline=True
        )
        embed.add_field(
            name="EVs",
            value=f"""
            **Health**: {ev_health}
            **Attack**: {ev_attack}
            **Defense**: {ev_defense}
            **Speed**: {ev_speed}
            **Accuracy**: {ev_accuracy}
            **Retrieval**: {ev_retrieval}
            """,
            inline=True
        )
        embed.add_field(
            name = "Item",
            value = f"{item}",
            inline = True
        )
        embed.add_field(
            name="Ability",
            value=f"{ability}",
            inline = True
        )
        embed.set_footer(
            text = f"Slinger: {slinger}"
        )
        embed.set_thumbnail(url=f"{imgurl}")
        # embed.set_footer(text = )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(
        description = "Gets information about the slug from the team",
    )
    async def charinfo(self, interaction: Interaction):
        
        embed = discord.Embed(
            title = "Character Info",
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(SlugInfo(bot))

