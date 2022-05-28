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

        # Autocorrects the slug name using the slug list
        slug_name = autolist.autocorrect(slug_name,slugs_list)

        if slug_name == "all":
            all_embed = discord.Embed(
                title = "All Slugs",
                color = ctx.bot.main
            )
            all_embed = discord.Embed(
                name = "Slugs List",
                value = f"""
                    {slugs_list[0]}    {slugs_list[1]}    {slugs_list[2]}
                    {slugs_list[3]}    {slugs_list[4]}    {slugs_list[5]}
                    {slugs_list[6]}    {slugs_list[7]}    {slugs_list[8]}
                    {slugs_list[9]}    {slugs_list[10]}    {slugs_list[11]}
                """,
            )
            return await ctx.send(embed=all_embed)

        # Checks if slug name exists
        if slug_name in slugs_list:
            slugdata = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1",slug_name)

            slug_emoji = slugdata[0]['slugemoji']
            typeid = slugdata[0]['slugtypeid']
            type = slugdata[0]['type']
            rarity = slugdata[0]['rarity']
            location = slugdata[0]['location']
            desc = slugdata[0]['description']
            ghoul = slugdata[0]['ghoul']
            protoimgurl = slugdata[0]['protoimgurl']
            attack = slugdata[0]['attack']
            speed = slugdata[0]['speed']

            type_emoji, embed_color = await self.types(ctx, type)
            rarity_emoji, stars = await self.rarities(ctx, rarity.lower())

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
                    **Attack**: {attack}
                    **Speed**: {speed}
                """,
                inline=False
            )
            info_embed.set_thumbnail(
                url = f"{protoimgurl}"
            )
            info_embed.set_author(name=f"{stars}")
            info_embed.set_footer(text=f"Ghoul - {ghoul.capitalize()} #{typeid}G")
            await ctx.send(embed=info_embed)

        else:
            await ctx.send(f"No slug named {slug_name} found.")

def setup(bot):
    bot.add_cog(Slug_Details(bot))
