import discord
from discord.ext import commands
import autolist

class Slug_Details(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def sl(self, coln, posn, authorid):

        author = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", authorid)
        if not author:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold, crystal, gem) VALUES ($1, $2, $3, $4)",
                                          authorid, 0, 0, 0)
        author = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", authorid)

        position = str(coln) + "-" + str(posn)
        allslugs = await self.bot.pg_con.fetch("SELECT * FROM allslugs WHERE container_position = $1 and userid = $2", position,authorid)
        if not allslugs:
            return "\u2800\u2800"
        allslugs = await self.bot.pg_con.fetch("SELECT * FROM allslugs WHERE container_position = $1 and userid = $2", position,authorid)

        slugname = allslugs[0]['slugname']
        slugdata = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", slugname)

        slugemoji = slugdata[0]['slugemoji']
        # print(slugemoji)
        return slugemoji

    @commands.command(
        aliases= ['allslugs','as','box']
    )
    async def arsenal(self, ctx, n=1, user:discord.Member = None):
        if user is None:
            a = int(ctx.message.author.id)
        else:
            a = int(user.id)
        embed = discord.Embed(
            title="All Slugs",
            description=f"""
            🔷|\U0001f1e6|\U0001f1e7|\U0001f1e8|\U0001f1e9|\U0001f1ea
            1️⃣|{await self.sl(n, 'a1', a)}|{await self.sl(n, 'b1', a)}|{await self.sl(n, 'c1', a)}|{await self.sl(n, 'd1', a)}|{await self.sl(n, 'e1', a)}
            2️⃣|{await self.sl(n, 'a2', a)}|{await self.sl(n, 'b2', a)}|{await self.sl(n, 'c2', a)}|{await self.sl(n, 'd2', a)}|{await self.sl(n, 'e2', a)}
            3️⃣|{await self.sl(n, 'a3', a)}|{await self.sl(n, 'b3', a)}|{await self.sl(n, 'c3', a)}|{await self.sl(n, 'd3', a)}|{await self.sl(n, 'e3', a)}
            4️⃣|{await self.sl(n, 'a4', a)}|{await self.sl(n, 'b4', a)}|{await self.sl(n, 'c4', a)}|{await self.sl(n, 'd4', a)}|{await self.sl(n, 'e4', a)}
            5️⃣|{await self.sl(n, 'a5', a)}|{await self.sl(n, 'b5', a)}|{await self.sl(n, 'c5', a)}|{await self.sl(n, 'd5', a)}|{await self.sl(n, 'e5', a)}
            """,
            colour=ctx.bot.main)
        await ctx.send(embed=embed)

    async def types(self, ctx, type):
        if type == "fire":
            emoji = ctx.bot.fire
            color = discord.Colour.from_rgb(255, 102, 51)
        elif type == "water":
            emoji = "<:Water2:846955422224351232>"
            color = discord.Colour.from_rgb(0, 128, 255)
        elif type == "ice":
            emoji = "<:Ice2:846952072784248842>"
            color = discord.Colour.from_rgb(0, 255, 255)
        elif type == "energy":
            emoji = '<:Energy:846363402552344606>'
            color = discord.Colour.from_rgb(121, 255, 77)
        elif type == "electric":
            emoji = ctx.bot.electric
            color = ctx.bot.celectric
        elif type == "psychic":
            emoji =  ctx.bot.psychic
            color = ctx.bot.cpsychic
        elif type == "earth":
            emoji = ctx.bot.earth
            color = ctx.bot.cearth
        elif type == "metal":
            emoji = ctx.bot.metal
            color = ctx.bot.cmetal
        elif type == "plant":
            emoji = ctx.bot.plant
            color = ctx.bot.cplant
        elif type == "air":
            emoji = ctx.bot.air
            color = ctx.bot.cair
        elif type == "toxic":
            emoji = ctx.bot.toxic
            color = ctx.bot.ctoxic
        elif type == "dark":
            emoji = ctx.bot.dark
            color = ctx.bot.cdark
        else:
            emoji = ctx.bot.slugshot
            color = ctx.bot.main
        return emoji, color

    async def rarities(self, ctx, rarity: str):
        if rarity == 'common':
            remoji = ctx.bot.common
            stars = "⭐"
        elif rarity == 'uncommon':
            remoji = ctx.bot.uncommon
            stars = "⭐⭐"
        elif rarity == 'rare':
            remoji = ctx.bot.rare
            stars = "⭐⭐⭐"
        elif rarity == 'super rare':
            remoji = ctx.bot.super_rare
            stars = "⭐⭐⭐⭐"
        elif rarity == 'mythical':
            remoji = ctx.bot.mythical
            stars = "⭐⭐⭐⭐⭐"
        elif rarity == 'legendary':
            remoji = ctx.bot.legendary
            stars = "⭐⭐⭐⭐⭐⭐"
        else:
            remoji = ctx.bot.common
            stars = "?"
        return remoji, stars

    @commands.command(
        description = "Provides data regarding a specific slug",
        aliases = ['i']
    )
    async def info(self, ctx, *, slug_name):

        # Fetches a list of all slugs
        slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata")
        length = len(slugdatadb)
        slugs_list = []
        for i in range(0, length):
            slugs_list.append(slugdatadb[i]['slugname'])

        # todo : Needs Update
        if slug_name == "all":
            all_embed = discord.Embed(
                title = "All Slugs",
                color = ctx.bot.main
            )
            all_embed.add_field(
                name = "Slugs List",
                value = f"""
                    {slugs_list[0]},   {slugs_list[1]},    {slugs_list[2]}
                    {slugs_list[3]},    {slugs_list[4]},    {slugs_list[5]}
                    {slugs_list[6]},    {slugs_list[7]},    {slugs_list[8]}
                    {slugs_list[9]},    {slugs_list[10]},    {slugs_list[11]}
                """,
            )
            return await ctx.send(embed=all_embed)

        # Autocorrects the slug name using the slug list
        slug_name = autolist.autocorrect(slug_name,slugs_list)

        # Checks if slug name exists
        if slug_name not in slugs_list:
            return await ctx.send(f"No slug named {slug_name} found.")

        slugdata = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1",slug_name)

        slug_emoji = slugdata[0]['slugemoji']
        typeid = slugdata[0]['slugtypeid']
        type = slugdata[0]['type']
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

        type_emoji, embed_color = await self.types(ctx, type)
        rarity_emoji, stars = await self.rarities(ctx, rarity.lower())

        # region Ability Str
        ability_str = ''
        ability_countdb = (await self.bot.pg_con.fetchrow(
            "SELECT COUNT(slugname) FROM ability WHERE slugname = $1",
            slug_name
        ))['count']
        for i in range(0, ability_countdb+1):
            abilityno = i+1
            if abilityno == 1:
                ability_str += "**Base Ability :**\nDeals the normal base damage to the opposing slug\n"
                continue

            abilitydb = await self.bot.pg_con.fetchrow(
                "SELECT * FROM ability WHERE slugname = $1 AND abilityno = $2",
                slug_name, abilityno
            )
            ability_name = abilitydb['ability']
            ability_desc = abilitydb['desc']
            ability_rarity = abilitydb['rarity']
            ability_str += f"**{ability_name} ({ability_rarity}):**\n{ability_desc}\n"

        info_embed = discord.Embed(
            title = f"{slug_emoji} {slug_name.capitalize()} #{typeid}",
            description = f"{desc}",
            color = embed_color
        )
        info_embed.add_field(
            name = "Rarity",
            value = f"{rarity_emoji} {rarity.capitalize()}",
            inline=True
        )
        info_embed.add_field(
            name = "Type",
            value = f"{type_emoji} {type.capitalize()}",
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
        info_embed.add_field(
            name = "Abilities",
            value = f"{ability_str}",
            inline = False
        )
        info_embed.set_thumbnail(
            url = f"{protoimgurl}"
        )
        info_embed.set_author(name=f"{stars}")
        info_embed.set_footer(text=f"Ghoul - {ghoul.capitalize()} #{typeid}G")
        await ctx.send(embed=info_embed)

    async def profiledb(self, user_id):
        profiledb = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        if not profiledb:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold, crystal, gem) VALUES ($1, $2, $3, $4)",
                                          user_id, 0, 0, 0)
        profiledb = await self.bot.pg_con.fetchrow("SELECT * FROM profile WHERE userid = $1", user_id)
        return profiledb

    async def shopdb(self, user_id):
        shopdb = await self.bot.pg_con.fetchrow("SELECT * FROM shop WHERE userid = $1", user_id)
        if not shopdb:
            await self.bot.pg_con.execute("INSERT INTO shop(userid) VALUES ($1)",user_id)
        shopdb = await self.bot.pg_con.fetchrow("SELECT * FROM shop WHERE userid = $1", user_id)
        return shopdb

    @commands.command(
        description = "Activates the ability of a slug",
    )
    async def activate(self, ctx, ability_no: int, slug_no: int):
        user_id = int(ctx.message.author.id)
        profiledb = await self.profiledb(user_id)
        if slug_no == 1 or slug_no == 2 or slug_no == 3 or slug_no == 4:
            pass
        else:
            return await ctx.send("You have to mention a slug number ranging from 1 to 4")

        if ability_no == 1 or ability_no == 2 or ability_no == 3:
            pass
        else:
            return await ctx.send("You have to mention a ability number 1, 2 or 3 depending on the slug")

        slug_id = profiledb[f'team{slug_no}']
        if slug_id is None or slug_id == '':
            return await ctx.send("No slug at that position.")

        allslugsdb = await self.bot.pg_con.fetchrow(
            "SELECT * FROM allslugs WHERE slugid = $1",
            slug_id
        )
        slug_name = allslugsdb['slugname']

        current_abilityno = int(allslugsdb['abilityno'])
        if ability_no == current_abilityno:
            return await ctx.send("That ability is already activated.")

        abilitydb = await self.bot.pg_con.fetchrow(
            "SELECT * FROM ability WHERE slugname = $1 AND abilityno = $2",
            slug_name, ability_no
        )

        if not abilitydb:
            return await ctx.send(f"No such ability exists for {slug_name}")

        if ability_no == 1:
            await self.bot.pg_con.execute(
                "UPDATE allslugs SET abilityno = $1 WHERE slugid = $2",
                1, slug_id
            )
            end_embed = discord.Embed(
                description=f"Base Ability Activated for {slug_name}",
                color=ctx.bot.success
            )
            await ctx.send(embed=end_embed)

        abs = allslugsdb[f'ability{ability_no}']
        ability_name = abilitydb['ability']
        print(abs)
        # return
        if abs == 1:
            await self.bot.pg_con.execute(
                "UPDATE allslugs SET abilityno = $1 WHERE slugid = $2",
                ability_no, slug_id
            )
            end_embed = discord.Embed(
                description = f"{ability_name} Ability Activated for {slug_name}",
                color = ctx.bot.success
            )
            await ctx.send(embed=end_embed)

        elif abs == 0:
            ab_rarity = abilitydb['rarity']

            shopdb = await self.shopdb(user_id)
            keys = shopdb[f'{ab_rarity.lower()}_key']

            if keys < 1:
                return await ctx.send(f"No {ab_rarity} Keys. You need a {ab_rarity} key to unlock the {ability_name} ability.")

            await self.bot.pg_con.execute(
                f"UPDATE shop SET {ab_rarity.lower()}_key = $1 WHERE userid = $2",
                keys - 1, user_id
            )
            await self.bot.pg_con.execute(
                f"UPDATE allslugs SET ability{ability_no} = $1 WHERE slugid = $2",
                1, slug_id
            )

            # activating it
            await self.bot.pg_con.execute(
                "UPDATE allslugs SET abilityno = $1 WHERE slugid = $2",
                ability_no, slug_id
            )
            end_embed = discord.Embed(
                description=f"{ability_name} Ability Activated for {slug_name}",
                color=ctx.bot.success
            )
            await ctx.send(embed=end_embed)

        else:
            await ctx.send("Processing...")

async def setup(bot):
    await bot.add_cog(Slug_Details(bot))
