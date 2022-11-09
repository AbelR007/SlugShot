import discord
from discord.ext import commands
import autolist
import consts as c
from exts import items
# Slash Command Modules
from discord import Interaction, app_commands

""" SlugDEX [Slashed]
- /dex | /slugdex
- /slug [slug]
- /char [character]
- /item [item]
"""

def types(type):
    if type == "fire":
        emoji = c.emoji_fire
        color = c.embed_fire
    elif type == "water":
        emoji = c.emoji_water
        color = c.embed_water
    elif type == "ice":
        emoji = c.emoji_ice
        color = c.embed_ice
    elif type == "energy":
        emoji = c.emoji_energy
        color = c.embed_energy
    elif type == "electric":
        emoji = c.emoji_electric
        color = c.embed_electric
    elif type == "psychic":
        emoji = c.emoji_psychic
        color = c.embed_psychic
    elif type == "earth":
        emoji = c.emoji_earth
        color = c.embed_earth
    elif type == "metal":
        emoji = c.emoji_metal
        color = c.embed_metal
    elif type == "plant":
        emoji = c.emoji_plant
        color = c.embed_plant
    elif type == "air":
        emoji = c.emoji_air
        color = c.embed_air
    elif type == "toxic":
        emoji = c.emoji_toxic
        color = c.embed_toxic
    elif type == "dark":
        emoji = c.emoji_dark
        color = c.embed_dark
    else:
        emoji = c.slugshot
        color = c.main_color
    return emoji, color

def rarities(rarity):
    if rarity == 'common':
        remoji = c.emoji_common
        stars = "⭐"
    elif rarity == 'uncommon':
        remoji = c.emoji_uncommon
        stars = "⭐⭐"
    elif rarity == 'rare':
        remoji = c.emoji_rare
        stars = "⭐⭐⭐"
    elif rarity == 'super rare':
        remoji = c.emoji_super_rare
        stars = "⭐⭐⭐⭐"
    elif rarity == 'mythical':
        remoji = c.emoji_mythical
        stars = "⭐⭐⭐⭐⭐"
    elif rarity == 'legendary':
        remoji = c.emoji_legendary
        stars = "⭐⭐⭐⭐⭐⭐"
    else:
        remoji = c.emoji_common
        stars = "NA"
    return remoji, stars

class SlugDexCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(
        name = "dex",
        description = "The Great SlugDeX containing everything",
    )
    async def slugdex_command(self, interaction: Interaction):

        server = interaction.guild

        total_slugs = len(await self.bot.pg_con.fetch("SELECT * FROM slugdata"))
        total_chars = len(await self.bot.pg_con.fetch("SELECT * FROM chardata"))
        total_items = len(await self.bot.pg_con.fetch("SELECT * FROM shop")) - 1

        prefix = (await self.bot.pg_con.fetchrow("SELECT * FROM server WHERE serverid = $1", server.id))["prefix"]

        embed = discord.Embed(
            title = "SlugDeX",
            description = "The Great SlugDex containing all information about slugs and characters and items",
            color = c.main
        )
        embed.add_field(
            name = "Slugs Command",
            value = f"`{prefix}slug [slug name]`\n`{prefix}slug infurnus`",
            inline = True
        )
        embed.add_field(
            name = "Characters Command",
            value = f"`{prefix}char [character name]`\n`{prefix}char Eli Shane`",
            inline = True
        )
        embed.add_field(
            name = "Items Command",
            value = f"`{prefix}item [item name]`\n`{prefix}item Damage Enhancer`",
            inline = True
        )
        embed.add_field(
            name = "Total Slugs",
            value = f"{total_slugs}",
            inline = True
        )
        embed.add_field(
            name = "Total Characters",
            value = f"{total_chars}",
            inline = True
        )
        embed.add_field(
            name = "Total Items",
            value = f"{total_items}",
            inline = True
        )
        await interaction.response.send_message(embed = embed)
    
    @app_commands.command(
        name = "slug",
        description="Shows the list of all pokemon",
    )
    @app_commands.rename(
        slug_name = "slug",
    )
    @app_commands.describe(
        slug_name = "Specify the slug name",
    )
    async def slug_command(self, interaction: Interaction, slug_name: str = None):

        db_slugdata = await self.bot.pg_con.fetch("SELECT * FROM slugdata")
        length = len(db_slugdata)
        slugs_list = []

        if not slug_name:
            list_embed = discord.Embed(
                title = "SlugDEX",
                description = f"List of all {length} pokemon",
                color = c.main
            )
            # list1
            list_embed.add_field(
                name="\u2800",
                value="this",
                inline=True
            )
            # list2
            list_embed.add_field(
                name = "\u2800",
                value = "this",
                inline = True
            )
            # list 3
            list_embed.add_field(
                name = "\u2800",
                value = "this",
                inline = True
            )
            await interaction.response.send_message(embed = list_embed)
            return
        
        for i in range(0, length):
            slugs_list.append(db_slugdata[i]['slugname'])
        
        # Autocorrects
        slug_name = autolist.autocorrect(slug_name, slugs_list)

        # Checks if slug name exists in database
        if slug_name not in slugs_list:
            return await interaction.response.send_message(f"No slug named {slug_name} was found.")
        
        # Gets slug data
        slugdata = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1",slug_name)

        slug_emoji = slugdata[0]['slugemoji']
        typeid = slugdata[0]['slugtypeid']
        slug_type = slugdata[0]['type']
        rarity = slugdata[0]['rarity']
        location = slugdata[0]['location']
        desc = slugdata[0]['description']
        ghoul = slugdata[0]['ghoul']
        protoimgurl = slugdata[0]['protoimgurl']

        health = slugdata[0]['health']
        attack = slugdata[0]['attack']
        defense = slugdata[0]['defense']
        speed = slugdata[0]['speed']
        accuracy = slugdata[0]['accuracy']
        retrieval = slugdata[0]['retrieval']

        # Gets type data
        type_emoji, embed_color = types(slug_type)
        rarity_emoji, stars = rarities(rarity.lower())

        # Slugdex embed
        info_embed = discord.Embed(
            title = f"{type_emoji} {slug_name.capitalize()} #{typeid}",
            description = f"*{desc}*",
            color = embed_color
        )
        info_embed.add_field(
            name = "Rarity",
            value = f"{rarity_emoji} {rarity.capitalize()}",
            inline=True
        )
        info_embed.add_field(
            name = "Type",
            value = f"{type_emoji} {slug_type.capitalize()}",
            inline=True
        )
        info_embed.add_field(
            name = "Location",
            value = f"{location}",
            inline=True
        )
        info_embed.add_field(
            name= "Base Stats",
            value=f"""
                **Health**: {health}
                **Attack**: {attack}
                **Speed**: {speed}
            """,
            inline = True
        )
        info_embed.add_field(
            name = "\u2800",
            value = f"""
                **Defense**: {defense}
                **Accuracy**: {accuracy}
                **Retrieval**: {retrieval}
           """,
            inline = True
        )
        # info_embed.add_field(
        #     name = "Abilities",
        #     value = f"{ability_str}",
        #     inline = False
        # )
        info_embed.set_thumbnail(
            url = f"{protoimgurl}"
        )
        info_embed.set_author(name=f"{stars}")
        info_embed.set_footer(text=f"Ghoul - {ghoul.capitalize()} #{typeid}G")
        
        await interaction.response.send_message(embed=info_embed)
    
    @app_commands.command(
        description = "Shows the description about the characters",
    )
    @app_commands.rename(
        char_name = "character"
    )
    @app_commands.describe(
        char_name = "Specify the character name"
    )
    async def char(self, interaction: Interaction, *, char_name: str = None):
        
        db_chardata = await self.bot.pg_con.fetch("SELECT * FROM chardata")
        length = len(db_chardata)
        chars_list = []

        if not char_name:
            return await interaction.response.send_message("Specify a character name.")
        
        # Char List
        for i in range(0, length):
            chars_list.append(db_chardata[i]['charname'])
        
        # Autocorrects
        char_name = autolist.autocorrect(char_name, chars_list)

        if char_name not in chars_list:
            return await interaction.response.send_message(f"No character named {char_name} found")
        
        # Gets char data
        chardata = await self.bot.pg_con.fetchrow("SELECT * FROM chardata WHERE charname = $1",char_name)

        type_id = chardata['chartypeid']
        desc = chardata['description']
        rarity = chardata['rarity']
        ch_class = chardata['class']
        imgurl = chardata['imgurl']
        type_enhancer = chardata['type_enhancer']
        # char_type = chardata['type']

        health = chardata['health']
        attack = chardata['attack']
        defense = chardata['defense']
        speed = chardata['speed']
        accuracy = chardata['accuracy']
        # retrieval = chardata['retrieval']

        slug1 = chardata['slug1'].capitalize()
        slug2 = chardata['slug2'].capitalize()
        slug4 = chardata['slug4'].capitalize()
        slug3 = chardata['slug3'].capitalize()

        # Gets data from functions
        rarity_emoji, stars = rarities(rarity.lower())

        # Character Data Embed
        char_embed = discord.Embed(
            title = f"{char_name.capitalize()} #{type_id}",
            description = f"*{desc}*",
            color = c.main
        )
        char_embed.add_field(
            name = "Rarity",
            value = f"{rarity_emoji} {rarity.capitalize()}",
            inline = True
        )
        char_embed.add_field(
            name = "Class",
            value = f"{ch_class}",
            inline = True
        )
        char_embed.add_field(
            name = "Type Enhancer",
            value = f"{type_enhancer}",
            inline = True
        )
        # more info : Residence or Mecha Beast he uses or Favourite Slug
        # Type Improvements
        # Abilities
        char_embed.add_field(
            name= "Base Stats",
            value=f"""
                **Health**: {health}
                **Attack**: {attack}
                **Speed**: {speed}
            """,
            inline = True
        )
        char_embed.add_field(
            name = "\u2800",
            value = f"""
                **Defense**: {defense}
                **Accuracy**: {accuracy}

           """,
            inline = True
        )
        char_embed.add_field(
            name = "Signature Slugs",
            value = f"**{slug1}** | {slug2} | {slug3} | {slug4}",
            inline = False
        )
        char_embed.set_thumbnail(
            url = f"{imgurl}"
        )
        char_embed.set_author(
            name = f"{stars}"
        )
        await interaction.response.send_message(embed = char_embed)
    
    @app_commands.command(
        description = "Shows the description about the slugs",
    )
    @app_commands.rename(
        item_name = "item"
    )
    @app_commands.describe(
        item_name = "Specify the item name"
    )
    async def item(self, interaction: Interaction, item_name: str = None):
        user = interaction.user

        if not item_name:
            return await interaction.response.send_message("Specify an item name.")
        
        items_list = list(items.keys())
        item_name = autolist.autocorrect(item_name, items_list)

        if item_name not in items_list:
            return await interaction.response.send_message(f"No item found named {item_name}.")
        
        # Gets item data
        cost = items[item_name][0]
        emoji = items[item_name][1]
        desc = items[item_name][2]
        sell_cost = cost - int(cost * (40/100))

        embed = discord.Embed(
            title = f"{emoji} {item_name.title()}",
            description = f"{desc}",
            color = c.main
        )
        embed.add_field(
            name = "Buy Cost",
            value = f"{cost}{c.gold}",
            inline = True
        )
        embed.add_field(
            name = "Sell Cost",
            value = f"{sell_cost}{c.gold}",
            inline = True
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(SlugDexCog(bot))

