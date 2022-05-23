import discord
from discord.ext import commands
import random

class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # todo : add accuracy, defense stats to characters
    # todo : add characters

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

    async def final_embed(self, ctx, char_name, opp_name):
        final_embed = discord.Embed(
            title=f"{opp_name} lost. You won!",
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
            # slug_attack = slugdatadb[0]['attack']
            # slugs_list.remove(f"{slug_name}")
        elif choice == 2:
            slug_name = random.choice(slugs_list)
            # slug_attack = 120
            # slug_speed = 110
        elif choice == 3:
            slug_name = random.choice(slugs_list)
            # slug_attack = 150
            # slug_speed = 90
        elif choice == 4:
            slug_name = random.choice(slugs_list)
            # slug_attack = 130
            # slug_speed = 60
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

    @commands.command()
    async def bsdk(self, ctx):
        slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata")
        length = len(slugdatadb)
        slugs_list = []
        for i in range(0,length):
            slugs_list.append(slugdatadb[i]['slugname'])

        slug_name = random.choice(slugs_list)
        slugs_list.remove(f"{slug_name}")
        main_slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", slug_name)
        slug_attack = main_slugdatadb[0]['attack']
        await ctx.send(f"{slug_name}\n{slugs_list}\n{slug_attack}")

    @commands.command()
    async def new(self, ctx):
        slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata")
        await ctx.send(f"{slugdatadb['infurnus']['slugname']}")

    @commands.command(
        description = "Battle with the AI",
        aliases = ['bb','battle']
    )
    async def botbattle(self, ctx):
        user_id = int(ctx.message.author.id)

        profiledb = await self.profiledb(user_id)

        char_name = "Eli Shane"
        char_id = 1
        char_health = 1000

        opp_name = "Will Shane"
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

            if opp_slug_speed > slug_speed:
                char_health = char_health - opp_slug_attack
                if char_health <= 0:
                    await self.last_result_embed(ctx, char_name, opp_name, opp_slug_name, char_health)
                    await self.final_embed(ctx, char_name, opp_name)
                    return
                else:
                    await self.result_embed(ctx, char_name, opp_name, opp_slug_name, opp_slug_attack, slug_name, slug_attack)
                opp_health = opp_health - slug_attack

            elif slug_speed > opp_slug_speed:
                opp_health = opp_health - slug_attack
                if opp_health <= 0:
                    await self.last_result_embed(ctx, char_name, opp_name, slug_name, opp_health)
                    await self.final_embed(ctx, char_name, opp_name)
                    return
                else:
                    await self.result_embed(ctx, char_name, opp_name, slug_name, slug_attack, opp_slug_name, opp_slug_attack)
                char_health = char_health - opp_slug_attack

            else: # when slug_speed == opp_slug_speed
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
                    await self.result_embed(ctx, char_name, opp_name, slug_name, slug_attack, opp_slug_name, opp_slug_attack)
        # The END of Battle

    # @commands.command()
    # async def botbattle(self, ctx):
    #
    #     char_name = "Eli Shane"
    #     char_id = 1
    #     char_health = 1000
    #
    #     opp_name = "Will Shane"
    #     opp_id = 2
    #     opp_health = 900
    #
    #     slug1_name = "infurnus".capitalize()
    #     slug1_attack = 130
    #     slug1_speed = 100
    #
    #     slug2_name = "".capitalize()
    #     slug2_attack = 200
    #     slug2_speed = 80
    #
    #     slug3_name = "".capitalize()
    #     slug3_attack = 300
    #     slug3_speed = 50
    #
    #     slug4_name = "".capitalize()
    #     slug4_attack = 400
    #     slug4_speed = 90
    #
    #     opp_slug1_name = "aquabeek".capitalize()
    #     opp_slug1_attack = 90
    #     opp_slug1_speed = 50
    #
    #     opp_slug2_name = "aquabeek two".capitalize()
    #     opp_slug2_attack = 70
    #     opp_slug1_speed = 60
    #
    #     opp_slug3_name = "aquabeek ts".capitalize()
    #     opp_slug3_attack = 30
    #     opp_slug1_speed = 90
    #
    #     opp_slug4_name = "aquabeek four".capitalize()
    #     opp_slug4_attack = 60
    #     opp_slug1_speed = 40
    #
    #     while True:
    #         # Battle Embed
    #         await self.battle_embed(ctx, char_name, char_health, opp_name, opp_health)
    #
    #         # Input Check
    #         def check(a):
    #             return a.author == ctx.message.author
    #
    #         # Waiting for User's Command
    #         msg = await self.bot.wait_for('message', check=check)
    #         choice = int(msg.content)
    #
    #         # Characters's Choice of Slug
    #         choice = int(random.randint(1,4))
    #
    #         # Choice Options
    #         if choice == 1:
    #             await self.choice_embed(ctx, slug1_name)
    #             opp_health = opp_health - slug1_attack
    #
    #             if opp_health <= 0:
    #                 await self.last_result_embed(ctx, slug1_name, opp_health)
    #                 await self.final_embed(ctx, opp_name)
    #                 return
    #             else:
    #                 await self.result_embed(ctx, slug1_name,slug1_attack)
    #
    #         elif choice == 2:
    #             await self.choice_embed(ctx, slug2_name)
    #             opp_health = opp_health - slug2_attack
    #
    #             if opp_health <= 0:
    #                 await self.last_result_embed(ctx, slug2_name, opp_health)
    #                 await self.final_embed(ctx, opp_name)
    #                 return
    #             else:
    #                 await self.result_embed(ctx, slug2_name,slug2_attack)
    #
    #         elif choice == 3:
    #             await self.choice_embed(ctx, slug3_name)
    #             opp_health = opp_health - slug3_attack
    #
    #             if opp_health <= 0:
    #                 await self.last_result_embed(ctx, slug3_name, opp_health)
    #                 await self.final_embed(ctx, opp_name)
    #                 return
    #             else:
    #                 await self.result_embed(ctx, slug3_name, slug3_attack)
    #
    #         elif choice == 4:
    #             await self.choice_embed(ctx, slug4_name)
    #             opp_health = opp_health - slug4_attack
    #
    #             if opp_health <= 0:
    #                 await self.last_result_embed(ctx, slug4_name, opp_health)
    #                 await self.final_embed(ctx, opp_name)
    #                 return
    #             else:
    #                 await self.result_embed(ctx, slug4_name, slug4_attack)
    #
    #         else:
    #             return await ctx.send("Illegal.")
    #
    #     # The END of Battle

    # todo : contain all database files in a function

    @commands.command()
    async def battleon(self, ctx):
        user_id = int(ctx.message.author.id)


        profile = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        if not profile:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold, crystal, gem) VALUES ($1, $2, $3, $4)",
                                          user_id, 0, 0, 0)
        profile = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)

        slug1_id = profile[0]['team1']
        slug2_id = profile[0]['team2']
        slug3_id = profile[0]['team3']
        slug4_id = profile[0]['team4']

        allslugsdb_1 = await self.bot.pg_con.fetch("SELECT * FROM allslugs where slugid = $1", slug1_id)
        allslugsdb_2 = await self.bot.pg_con.fetch("SELECT * FROM allslugs where slugid = $1", slug2_id)
        allslugsdb_3 = await self.bot.pg_con.fetch("SELECT * FROM allslugs where slugid = $1", slug3_id)
        allslugsdb_4 = await self.bot.pg_con.fetch("SELECT * FROM allslugs where slugid = $1", slug4_id)



        slug1_name = allslugsdb_1[0]['slugname']
        slug2_name = allslugsdb_2[0]['slugname']
        slug3_name = allslugsdb_3[0]['slugname']
        slug4_name = allslugsdb_4[0]['slugname']

        slugdatadb_1 = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1",slug1_name)
        slugdatadb_2 = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1",slug2_name)
        slugdatadb_3 = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1",slug3_name)
        slugdatadb_4 = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1",slug4_name)

        slug1_attack = slugdatadb_1[0]['attack']
        slug2_attack = slugdatadb_2[0]['attack']
        slug3_attack = slugdatadb_3[0]['attack']
        slug4_attack = slugdatadb_4[0]['attack']


        # Characters Health & Details
        char_name = "Eli Shane"
        char_id = 1
        char_health = 1000

        opp_name = random.choice(["Will Shane","Tad","Dr Blakk"])
        opp_id = 2
        opp_health = random.randint(700,1100)

        # slug1_name = "infurnus".capitalize()
        # slug1_attack = 130
        #
        # slug2_name = "".capitalize()
        # slug2_attack = 200
        #
        # slug3_name = "".capitalize()
        # slug3_attack = 300
        #
        # slug4_name = "".capitalize()
        # slug4_attack = 400

        while True:
            # Battle Embed
            await self.battle_embed(ctx, char_name, char_health, opp_name, opp_health)

            # Input Check
            def check(a):
                return a.author == ctx.message.author

            # Waiting for User's Command
            msg = await self.bot.wait_for('message', check=check)
            choice = int(msg.content)

            # Choice Options
            if choice == 1:
                await self.choice_embed(ctx, slug1_name)
                opp_health = opp_health - slug1_attack

                if opp_health <= 0:
                    await self.last_result_embed(ctx, slug1_name, opp_health)
                    await self.final_embed(ctx, opp_name)
                    return
                else:
                    await self.result_embed(ctx, slug1_name, slug1_attack)

            elif choice == 2:
                await self.choice_embed(ctx, slug2_name)
                opp_health = opp_health - slug2_attack

                if opp_health <= 0:
                    await self.last_result_embed(ctx, slug2_name, opp_health)
                    await self.final_embed(ctx, opp_name)
                    return
                else:
                    await self.result_embed(ctx, slug2_name, slug2_attack)

            elif choice == 3:
                await self.choice_embed(ctx, slug3_name)
                opp_health = opp_health - slug3_attack

                if opp_health <= 0:
                    await self.last_result_embed(ctx, slug3_name, opp_health)
                    await self.final_embed(ctx, opp_name)
                    return
                else:
                    await self.result_embed(ctx, slug3_name, slug3_attack)

            elif choice == 4:
                await self.choice_embed(ctx, slug4_name)
                opp_health = opp_health - slug4_attack

                if opp_health <= 0:
                    await self.last_result_embed(ctx, slug4_name, opp_health)
                    await self.final_embed(ctx, opp_name)
                    return
                else:
                    await self.result_embed(ctx, slug4_name, slug4_attack)

            else:
                return await ctx.send("Illegal.")

        # The END of Battle


def setup(bot):
    bot.add_cog(Battle(bot))