import discord
from discord.ext import commands
import random


class Explore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def battle_embed(self, ctx, char_name, char_health, opp_name, opp_health):
        battle_embed = discord.Embed(
            title=f"{char_name} VS {opp_name}",
            color=ctx.bot.main
        )
        battle_embed.add_field(
            name=f"{char_name}",
            value=f"Health : {char_health}",
            inline=False
        )
        battle_embed.add_field(
            name=f"{opp_name}",
            value=f"Health : {opp_health}",
            inline=False
        )
        battle_embed.set_footer(text="Choose a number 1, 2, 3 or 4 to shoot a slug")
        await ctx.send(embed=battle_embed)

    async def choice_embed(self, ctx, char_name, slug_name):
        choice_embed = discord.Embed(
            color=ctx.bot.main
        )
        choice_embed.set_author(name=f"{char_name} chose {slug_name}")
        await ctx.send(embed=choice_embed)

    async def result_embed(self, ctx, char_name, opp_name, first_slug_name, first_slug_attack, sec_slug_name, sec_slug_attack):
        result_embed = discord.Embed(
            description= f"""
            {first_slug_name} dealt {first_slug_attack} damage.
            {sec_slug_name} dealt {sec_slug_attack} damage.
            """,
            color=ctx.bot.main
        )
        result_embed.set_author(name=f"{char_name} vs {opp_name}")
        await ctx.send(embed=result_embed)

    async def last_result_embed(self, ctx, char_name, opp_char_name, slug_name, opp_health):
        last_result_embed = discord.Embed(
            title=f"{slug_name} dealt {abs(opp_health)} damage",
            color=ctx.bot.main
        )
        last_result_embed.set_author(name=f"{char_name} VS {opp_char_name}")
        await ctx.send(embed=last_result_embed)

    async def final_embed(self, ctx, char_name, opp_name,coins):
        final_embed = discord.Embed(
            title = "Final Results of the Battle",
            description =
            f"""
            {opp_name} lost. You won!
            {char_name} received {coins}{ctx.bot.coins} coins.
            """,
            color=ctx.bot.main
        )
        final_embed.set_author(name=f"{char_name} VS {opp_name}")
        await ctx.send(embed=final_embed)

    async def opp_choice(self, choice):
        slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata")
        length = len(slugdatadb)
        slugs_list = []
        for i in range(0, length):
            slugs_list.append(slugdatadb[i]['slugname'])

        if choice == 1:
            slug_name = random.choice(slugs_list)
        elif choice == 2:
            slug_name = random.choice(slugs_list)
        elif choice == 3:
            slug_name = random.choice(slugs_list)
        elif choice == 4:
            slug_name = random.choice(slugs_list)
        else:
            return None
        main_slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", slug_name)
        slug_attack = main_slugdatadb[0]['attack']
        slug_speed = main_slugdatadb[0]['speed']
        return slug_name, slug_attack, slug_speed

    async def profiledb(self, user_id):
        profile = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        if not profile:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold, crystal, gem) VALUES ($1, $2, $3, $4)",
                                          user_id, 0, 0, 0)
        profile = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        return profile



    async def battle(self, ctx, profiledb):
        user_id = int(ctx.message.author.id)

        location_char = {
            "Wild Spores Cavern": {
                "Kord": ['rammstone', 'hop rock', 'grenuke', 'thresher'],
                "Trixie": ['tormato', 'arachnet', 'polero', 'frostcrawler'],
                "Pronto": ['flatulorhinkus', 'jellyish', 'lariat', 'bubbaleone'],
            }
        }

        current_coins = profiledb[0]['coins']
        region = profiledb[0]['region']
        location = profiledb[0]['location']
        if location == "Shane Hideout":
            location = "Wild Spores Cavern"

        chars = location_char[location]
        chars = list(chars.keys())
        opp_name = random.choice(chars)

        char_name = "Eli Shane"
        char_id = 1
        char_health = 1000

        # opp_name = "Will Shane"
        opp_id = 2
        opp_health = 900

        while True:
            # Battle Embed
            await self.battle_embed(ctx, char_name, char_health, opp_name, opp_health)

            # Input Check
            def check(a):
                return a.author == ctx.message.author

            # Waiting for User's Command
            msg = await self.bot.wait_for('message', check=check)
            choice = int(msg.content)

            # Opponent Character's Choice of Slug
            opp_choice = int(random.randint(1, 4))
            opp_slug_name, opp_slug_attack, opp_slug_speed = await self.opp_choice(opp_choice)
            # print(opp_slug_name, opp_slug_attack, opp_slug_speed)

            # Choice Options
            if choice == 1:
                slug_id = profiledb[0]['team1']
            elif choice == 2:
                slug_id = profiledb[0]['team2']
            elif choice == 3:
                slug_id = profiledb[0]['team3']
            elif choice == 4:
                slug_id = profiledb[0]['team4']
            else:
                return await ctx.send("Enter a valid option")
            # it returns slug name and slug total attack
            allslugsdb = await self.bot.pg_con.fetch("SELECT * FROM allslugs WHERE slugid = $1", slug_id)
            slug_name = allslugsdb[0]['slugname']
            slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", slug_name)
            slug_attack = slugdatadb[0]['attack']
            slug_speed = slugdatadb[0]['speed']

            # it returns opponent's slug name and slug attack
            await self.choice_embed(ctx, char_name, slug_name)

            # Battle Calculations
            # opp_health = opp_health - slug_attack
            # char_health = char_health - opp_slug_attack

            coins = random.randint(20, 50)

            if opp_slug_speed > slug_speed:
                char_health = char_health - opp_slug_attack
                if char_health <= 0:

                    await self.last_result_embed(ctx, char_name, opp_name, opp_slug_name, char_health)
                    await self.final_embed(ctx, char_name, opp_name, coins)
                    return
                else:
                    await self.result_embed(ctx, char_name, opp_name, opp_slug_name, opp_slug_attack, slug_name,
                                            slug_attack)
                opp_health = opp_health - slug_attack

            elif slug_speed > opp_slug_speed:
                opp_health = opp_health - slug_attack
                if opp_health <= 0:
                    await self.last_result_embed(ctx, char_name, opp_name, slug_name, opp_health)
                    await self.final_embed(ctx, char_name, opp_name, coins)
                    await self.bot.pg_con.execute("UPDATE profile SET coins = $1 WHERE userid = $2",coins + current_coins, user_id)
                    return
                else:
                    await self.result_embed(ctx, char_name, opp_name, slug_name, slug_attack, opp_slug_name,
                                            opp_slug_attack)
                char_health = char_health - opp_slug_attack

            else:  # when slug_speed == opp_slug_speed
                opp_health = opp_health - slug_attack
                char_health = char_health - opp_slug_attack
                if opp_health <= 0:
                    await self.last_result_embed(ctx, char_name, opp_name, slug_name, opp_health)
                    await self.final_embed(ctx, char_name, opp_name)
                    return
                elif char_health <= 0:
                    await self.last_result_embed(ctx, char_name, opp_name, opp_slug_name, char_health)
                    await self.final_embed(ctx, char_name, opp_name)
                    return
                else:
                    # Battle results after calculations
                    await self.result_embed(ctx, char_name, opp_name, slug_name, slug_attack, opp_slug_name,
                                            opp_slug_attack)

    @commands.command(
        description = "Explore the caverns",
        aliases = ['exp']
    )
    async def explore(self, ctx):
        user_id = int(ctx.message.author.id)
        profiledb = await self.profiledb(user_id)

        await self.battle(ctx, profiledb)
        # The END of Battle


def setup(bot):
    bot.add_cog(Explore(bot))