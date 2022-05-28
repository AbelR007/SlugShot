import asyncio

import autolist
import discord
from discord.ext import commands
from bot import bot as emo

items_list = {
    'fire slug food':
        [20,'<:fire_food:979751145343950888>','Slug food for the Fire Type Slugs'],
    'water slug food': [20,'<:water_food:979751175463247882>','Slug food for the Water Type Slugs'],
    'energy slug food': [20,'<:energy_food:979751168785940481>','Slug food for the Energy Type Slugs'],
    'earth slug food': [20,'<:earth_food:979751165648592956>','Slug food for the Earth Type Slugs'],
    'air slug food': [20,'<:air_food:979751161328439316>','Slug food for the Air Type Slugs'],

    'damage enhancer':
        [2000, emo.question_mark, "Increases damage of a slug by 10%. Efficient for a high damage dealing slug."],
    'defense boost':
        [2000, emo.question_mark, "Increases defense of a slug by 10%. Efficient for defending high damage slugs."],
    # 'common box','rare box','mythical box','legendary box'
}

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def error_embed(self, ctx, content):
        embed = discord.Embed(title="ERROR", description=f"{content}", color=ctx.bot.error)
        return await ctx.send(embed=embed)

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

    @commands.command(aliases=['market'])
    async def shop(self, ctx):
        user_id = int(ctx.message.author.id)
        shopdb = await self.shopdb(user_id)
        embed = discord.Embed(
            title = "Market",
            color = ctx.bot.main
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/979725346658197524/979726475894849586/1653655381429.png"
        )
        #region Prints the list of items in the Shop
        for name in items_list:
            cost = items_list[name][0]
            emoji = items_list[name][1]
            desc = items_list[name][2]

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
                    **Cost** : {cost}{ctx.bot.gold}
                    **Description** : {desc}
                """,
                inline = False
            )
        #endregion
        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx, no = 1, *, item):
        user_id = int(ctx.message.author.id)
        profiledb = await self.profiledb(user_id)
        shopdb = await self.shopdb(user_id)

        all_items = list(items_list.keys())
        item = autolist.autocorrect(item, all_items)

        cost = items_list[item][0] * no
        gold = profiledb['gold']

        if gold < cost:
            return await self.error_embed(ctx,f"Insufficient gold!\nYou need {cost-gold}{ctx.bot.gold} more gold")

        if item not in items_list:
            return await self.error_embed(ctx,f"No item called {item} exists!")

        embed1 = discord.Embed(
            title = f"Are you sure you want to buy {no} {item} for {cost}{ctx.bot.gold}?",
            color = ctx.bot.invis
        )
        msg = await ctx.send(embed=embed1)

        timeout_embed = discord.Embed(
            title = f"Timeout!",
            color = ctx.bot.error
        )

        tick = "\U00002611"
        cross = "\U0000274e"
        await msg.add_reaction(tick)
        await msg.add_reaction(cross)

        def check(reaction, user):
            return user == ctx.message.author and (
                    str(reaction.emoji) == tick or
                    str(reaction.emoji) == cross
            )

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            return await msg.edit(embed=timeout_embed)
        else:
            pass
        # endregion

        if str(reaction.emoji) == tick:
            gold_left = gold - cost
            item_name_in_db = item.replace(' ','_')
            await self.bot.pg_con.execute(
                "UPDATE profile SET gold = $1 WHERE userid = $2", gold_left, user_id
            )
            await self.bot.pg_con.execute(
                f"UPDATE shop SET {item_name_in_db} = $1 WHERE userid = $2", shopdb[item_name_in_db] + no, user_id
            )
            embed = discord.Embed(
                title = f"Done! You have bought {no} {item} for {cost}{ctx.bot.gold}!",
                color = ctx.bot.success
            )
            await msg.edit(embed=embed)
        else:
            cancel_embed = discord.Embed(
                title= "Cancelled!",
                color =ctx.bot.error
            )
            await msg.edit(embed=cancel_embed)

    @commands.command()
    async def sell(self, ctx, no=1, *, item):
        user_id = int(ctx.message.author.id)
        profiledb = await self.profiledb(user_id)
        shopdb = await self.shopdb(user_id)

        all_items = list(items_list.keys())
        item = autolist.autocorrect(item, all_items)


def setup(bot):
    bot.add_cog(Shop(bot))