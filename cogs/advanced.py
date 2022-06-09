import discord
import random
import asyncio
from discord.ext import commands, tasks

class Advanced_Battle_Modes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def profiledb(self, user_id):
        profiledb = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        if not profiledb:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold, crystal, gem) VALUES ($1, $2, $3, $4)",
                                          user_id, 0, 0, 0)
        profiledb = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        return profiledb

    # region Used by : battle() function
    async def character_data(self, char):
        health = int(char['health'])
        attack = int(char['attack'])
        defense = int(char['defense'])
        speed = char['speed']
        imgurl = char['imgurl']
        return health, attack, defense, speed, imgurl

    async def slug_emoji(self, slug_id):
        if slug_id == '' or slug_id is None:
            return " "
        allslugsdb = await self.bot.pg_con.fetch("SELECT * FROM allslugs WHERE slugid = $1", slug_id)
        slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1",
                                                 allslugsdb[0]['slugname'])
        slugemoji = slugdatadb[0]['slugemoji']
        return slugemoji

    async def rank_up(self, slug):
        cur_xp = slug['exp']
        cur_rank = slug['rank']
        # cur_coins = slug['coins']

        if cur_xp >= round((5 * (cur_rank ** 3)) / 4):
            await self.bot.pg_con.execute("UPDATE allslugs SET rank = $1 WHERE slugid = $2", cur_rank + 1,
                                          slug['slugid'])
            return True
        else:
            return False

    async def slug_exp(self, ctx, exp_str, slug_id, slug_exp):
        if slug_exp != 0:
            slug_db = await self.bot.pg_con.fetchrow("SELECT * FROM allslugs WHERE slugid = $1", slug_id)
            await self.bot.pg_con.execute(
                "UPDATE allslugs SET exp = $1 WHERE slugid = $2", slug_db['exp'] + slug_exp, slug_id
            )
            slug_emoji = await self.slug_emoji(slug_id)
            exp_str += f"\n{slug_emoji}{slug_db['slugname'].capitalize()} recieved {slug_exp} EXP"

            if slug_db['rank'] < 50:
                if await self.rank_up(slug_db):
                    embed = discord.Embed(
                        description=f"**Congrats!** {slug_db['slugname'].capitalize()} is now Rank {slug_db['rank'] + 1}",
                        color=ctx.bot.main)
                    await ctx.send(embed=embed)
        return exp_str

    async def you_won_embed(
            self, ctx, user_id, char_name, opp_name, slug_name, char_imgurl, gold_prize, gold,
            slug1_id, slug1_exp, slug2_id, slug2_exp, slug3_id, slug3_exp, slug4_id, slug4_exp
    ):
        exp_str = ""
        exp_str = await self.slug_exp(ctx, exp_str, slug1_id, slug1_exp)
        exp_str = await self.slug_exp(ctx, exp_str, slug2_id, slug2_exp)
        exp_str = await self.slug_exp(ctx, exp_str, slug3_id, slug3_exp)
        exp_str = await self.slug_exp(ctx, exp_str, slug4_id, slug4_exp)

        final_embed = discord.Embed(
            description=
            f"""
                    **{char_name} used {slug_name.capitalize()}**!
                    {opp_name} lost the rest of its health!

                    {char_name} won the battle! You won!
                    You recieved {gold_prize}{ctx.bot.coins} coins.
                    {exp_str}

                    **Good Game!**
                    """,
            color=ctx.bot.main
        )
        # final_embed.add_field(
        #     name = "EXP gained :",
        #     value = f"{slug_name} recieved {random_exp} EXP.",
        #     inline = False
        # )
        final_embed.set_author(name=f"Battle Results", url=f"{char_imgurl}")
        await ctx.send(embed=final_embed)
        await self.bot.pg_con.execute("UPDATE profile SET gold = $1 WHERE userid = $2", gold, user_id)

    async def you_lost_embed(self, ctx, char_name, opp_name, opp_imgurl, opp_slug_name):
        final_embed = discord.Embed(
            description=f"""
                        **{opp_name} used {opp_slug_name.capitalize()}**!
                        {char_name} lost the rest of its health!

                        {opp_name} won the battle! You lost!
                        Good Game!
                    """,
            color=ctx.bot.main
        )
        final_embed.set_author(name=f"Battle Results", url=f"{opp_imgurl}")
        await ctx.send(embed=final_embed)

    async def action_embed(self, ctx, first_name, first_slug_name, first_slug_damage, second_name, second_slug_name,
                           second_slug_damage):
        result_embed = discord.Embed(
            description=f"""
                **{first_name} used {first_slug_name}**!
                {first_slug_name.capitalize()} dealt {first_slug_damage} damage
                **{second_name} used {second_slug_name}**!                         
                {second_slug_name.capitalize()} dealt {second_slug_damage} damage
            """,
            color=ctx.bot.main
        )
        # result_embed.set_author(name=f"{first_name} vs {second_name}")
        await ctx.send(embed=result_embed)

    async def slugdata_specific(self, slug_name, stat):
        slugdata = await self.bot.pg_con.fetchrow("SELECT * FROM slugdata WHERE slugname = $1", slug_name)
        statdata = slugdata[f'{stat}']
        return statdata

    async def battle_algo(self, Attack, Defense, Base, IV, EV, Rank, Level):
        Base_Bonus = int((2 * Base + IV + (0.25 * EV)) * (1 / 2))
        Rank_Bonus = int((Base_Bonus * Rank * 0.01) + Rank / 2)
        Level_Bonus = int(((Base_Bonus * Level) / 50) + Level * 2)
        Rank_Level = int(Rank * Level * 0.05)

        Slug_Attack = int(Base_Bonus + Level_Bonus + Rank_Bonus + Rank_Level)
        Character_Bonus = int((Slug_Attack / 2 * (Attack / Defense) * 0.09))

        Total_Damage = Slug_Attack + Character_Bonus

        return Total_Damage

    async def accuracy_check(self, ran_accuracy, slug_accuracy, char_health, opp_total_damage, shield,
                             action_str, char_name, slug_name):
        if ran_accuracy < slug_accuracy:
            char_health = char_health - opp_total_damage
        else:
            if shield <= 0:
                shield = 0
                char_health -= opp_total_damage
            else:
                shield -= opp_total_damage
                if shield < 0:
                    shield = 0

        action_str += f"{slug_name.capitalize()} dealt {opp_total_damage} damage\n"
        return char_health, shield, action_str

    # endregion
    # region  Ability Calculations
    async def ability_calc(self, slug_name, slug_ability_no):
        abilitydb = await self.bot.pg_con.fetchrow(
            "SELECT * FROM ability WHERE abilityno = $1 AND slugname = $2", slug_ability_no, slug_name
        )
        # ability_damage = abilitydb['damage']
        ability_msg = abilitydb['battlemsg']

        if slug_name == "infurnus":
            if slug_ability_no == 2:
                # ability_msg = "shoots a fireball at Opponent's Shield"
                ability_used = 2

            else:
                ability_used = 0
        else:
            ability_used = 0
            ability_msg = None
            # return None
        return ability_used, ability_msg

    async def ability_battle_calc(
            self, slug_name, slug_ability_no, opp_shield, slug_ability_damage, opp_health, slug_total_damage
    ):
        if slug_name == "infurnus":
            if slug_ability_no == 2:
                # region Flash Fire
                if opp_shield > 0:
                    opp_shield -= slug_ability_damage
                    if opp_shield < 0:
                        opp_shield = 0
                else:
                    opp_health -= slug_ability_damage
                slug_total_damage = slug_total_damage - int(slug_ability_damage - slug_ability_damage/3)
                # endregion Flash Fire

        elif slug_name == 'rammstone':
            if slug_ability_no == 2:
                # region Battleup
                slug_total_damage = slug_total_damage + slug_ability_damage
                # endregion Battleup

        else:
            pass
        return opp_shield, opp_health, slug_total_damage

    async def ability_before_battle(self, slug_data):
        return slug_data

    async def ability_after_attack(self, slug_data, slug_name, slug_ability_no, ch):
        current_damage = slug_data[f'slug{ch}_base_attack']
        if slug_name == "rammstone":
            if slug_ability_no == 2:
                current_damage = current_damage + current_damage*(10/100)

            else:
                pass
        else:
            pass
        # Changes
        slug_data[f'slug{ch}_base_attack'] = int(current_damage)
        return slug_data
    # endregion

    async def battle(self, ctx, user_id, opp_char, opp_slug1, opp_slug2, opp_slug3, opp_slug4):
        profiledb = await self.profiledb(user_id)
        current_gold = int(profiledb[0]['gold'])
        gold_prize = random.randint(10,20)
        gold = gold_prize + current_gold

        # region User :  Character Details
        char_name = "Young Eli"
        chardb = await self.bot.pg_con.fetchrow("SELECT * FROM chardata WHERE charname = $1", char_name)
        char_health, char_attack, char_defense, char_speed, char_imgurl = await self.character_data(chardb)

        # Slug IDs & Emojis for Battle Card
        slug1_id = profiledb[0]['team1']
        slug1_name = (await self.bot.pg_con.fetchrow("SELECT * FROM allslugs WHERE slugid = $1", slug1_id))['slugname']
        slugemoji1 = await self.slug_emoji(slug1_id)

        slug2_id = profiledb[0]['team2']
        slug2_name = (await self.bot.pg_con.fetchrow("SELECT * FROM allslugs WHERE slugid = $1", slug2_id))['slugname']
        slugemoji2 = await self.slug_emoji(slug2_id)

        slug3_id = profiledb[0]['team3']
        slug3_name = (await self.bot.pg_con.fetchrow("SELECT * FROM allslugs WHERE slugid = $1", slug3_id))['slugname']
        slugemoji3 = await self.slug_emoji(slug3_id)

        slug4_id = profiledb[0]['team4']
        slug4_name = (await self.bot.pg_con.fetchrow("SELECT * FROM allslugs WHERE slugid = $1", slug4_id))['slugname']
        slugemoji4 = await self.slug_emoji(slug4_id)

        slug1_health = await self.slugdata_specific(slug1_name,'health')
        slug2_health = await self.slugdata_specific(slug2_name,'health')
        slug3_health = await self.slugdata_specific(slug3_name,'health')
        slug4_health = await self.slugdata_specific(slug4_name,'health')

        # endregion
        slug_data = {
            'slug1_name': slug1_name,
            'slug2_name': slug2_name,
            'slug3_name': slug3_name,
            'slug4_name': slug4_name,

            'slug1_base_attack': await self.slugdata_specific(slug1_name,'attack'),
            'slug2_base_attack': await self.slugdata_specific(slug2_name,'attack'),
            'slug3_base_attack': await self.slugdata_specific(slug3_name,'attack'),
            'slug4_base_attack': await self.slugdata_specific(slug1_name,'attack'),
        }
        # region Opponent : Character Details
        opp_name = opp_char
        oppchardb = await self.bot.pg_con.fetchrow("SELECT * FROM chardata WHERE charname = $1", opp_name)
        opp_health, opp_attack, opp_defense, opp_speed, opp_imgurl = await self.character_data(oppchardb)

        # Slug Emojis for Battle Card
        opp_slug1_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug1))[0][
            'slugemoji']
        opp_slug2_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug2))[0][
            'slugemoji']
        opp_slug3_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug3))[0][
            'slugemoji']
        opp_slug4_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug4))[0][
            'slugemoji']

        opp_slug1_health = await self.slugdata_specific(opp_slug1, 'health')
        opp_slug2_health = await self.slugdata_specific(opp_slug2, 'health')
        opp_slug3_health = await self.slugdata_specific(opp_slug3, 'health')
        opp_slug4_health = await self.slugdata_specific(opp_slug4, 'health')
        # endregion
        # region >>> Shield >>>
        shield = slug1_health + slug2_health + slug3_health + slug4_health
        opp_shield = opp_slug1_health + opp_slug2_health + opp_slug3_health + opp_slug4_health
        # endregion

        slug1_exp = slug2_exp = slug3_exp = slug4_exp = 0
        win = 0

        slug_data = await self.ability_before_battle(slug_data)
        while True:
            # print(slug_data)
            # region Part 1 : Battle Embed
            action_str = ""
            battle_embed = discord.Embed(
                title=f"{char_name} VS {opp_name}",
                color=ctx.bot.main
            )
            battle_embed.add_field(
                name=f"{char_name}",
                value=f"""
                    Shield : {shield}
                    Health : {char_health}
                    Slugs : {slugemoji1}{slugemoji2}{slugemoji3}{slugemoji4}""",
                inline=False
            )
            battle_embed.add_field(
                name=f"{opp_name}",
                value=f"""
                    Shield : {opp_shield}
                    Health : {opp_health}
                    Slugs : {opp_slug1_emoji}{opp_slug2_emoji}{opp_slug3_emoji}{opp_slug4_emoji}
                """,
                # value=f"Health : {opp_health}\nSlugs : {opp_slug1_emoji}{opp_slug2_emoji}{opp_slug3_emoji}{opp_slug4_emoji}",
                inline=False
            )
            battle_embed.set_footer(text="Choose your option : 1, 2, 3, 4 or 'ff'")
            bembed = await ctx.send(embed=battle_embed)
            # endregion
            # region Part 2 : Input for Choice of Slug
            def check(a):
                return a.author == ctx.message.author and (
                        (a.content == "1") or (a.content == "2") or (a.content == "3") or (a.content == "4") or (
                        a.content == "ff"))

            # Waiting for User's Command
            timeout_embed = discord.Embed(
                title="Timeout!",
                description="You didn't reply in 40 seconds! Battle ended.",
                color=ctx.bot.invis
            )
            try:
                msg = await self.bot.wait_for('message', timeout=40.0, check=check)
            except asyncio.TimeoutError:
                return await bembed.edit(embed=timeout_embed)
            else:
                pass
            choice = msg.content
            random_exp = random.randint(5, 20)

            if choice == "1":
                slug_id = slug1_id
                slug1_exp += random_exp
            elif choice == "2":
                slug_id = slug2_id
                slug2_exp += random_exp
            elif choice == "3":
                slug_id = slug3_id
                slug3_exp += random_exp
            elif choice == "4":
                slug_id = slug4_id
                slug4_exp += random_exp
            elif choice == "ff":
                return await ctx.send("You forfeit!")
            else:
                return await ctx.send("Enter a valid option | Retry later")
            ch = int(choice)

            if slug_id == '' or slug_id is None:
                await ctx.send(f"There is no slug at position {choice}")
                continue
            # endregion
            # region Part 3 : User & Opponent's Slug Details
            allslugsdb = await self.bot.pg_con.fetchrow("SELECT * FROM allslugs WHERE slugid = $1", slug_id)
            slug_name = allslugsdb['slugname']
            slugdata = await self.bot.pg_con.fetchrow("SELECT * FROM slugdata WHERE slugname = $1", slug_name)

            slug_level = allslugsdb['level']
            slug_rank = allslugsdb['rank']

            slug_health = slugdata['health']
            slug_base_attack = slug_data[f'slug{ch}_base_attack']  # slugdata['attack']
            slug_defense = slugdata['defense']
            slug_speed = slugdata['speed']
            slug_accuracy = slugdata['accuracy']

            slug_ability_no = allslugsdb['abilityno']

            abilitydb = await self.bot.pg_con.fetchrow(
                "SELECT * FROM ability WHERE abilityno = $1 AND slugname = $2", slug_ability_no, slug_name
            )
            if abilitydb:
                slug_ability_name = abilitydb['ability']
                slug_ability_damage = abilitydb['damage']
                ability_speed = abilitydb['attackspeed']
            else:
                slug_ability_name = None
                slug_ability_damage = 0

            # region Opponent's Choice of Slug
            opp_slug_name = random.choice([opp_slug1,opp_slug2,opp_slug3,opp_slug4])
            opp_slugdata = await self.bot.pg_con.fetchrow("SELECT * FROM slugdata WHERE slugname = $1", opp_slug_name)

            opp_slug_level = random.randint(1,10)
            opp_slug_rank = random.randint(1,50)

            opp_slug_health = opp_slugdata['health']
            opp_slug_attack = opp_slugdata['attack']
            opp_slug_defense = opp_slugdata['defense']
            opp_slug_speed = opp_slugdata['speed']
            opp_slug_accuracy = opp_slugdata['accuracy']

            opp_slug_ability_no = 2  # random.randint(1,2)

            opp_abilitydb = await self.bot.pg_con.fetchrow(
                "SELECT * FROM ability WHERE abilityno = $1 AND slugname = $2", opp_slug_ability_no, opp_slug_name
            )
            if opp_abilitydb:
                opp_slug_ability_name = opp_abilitydb['ability']
                opp_slug_ability_damage = opp_abilitydb['damage']
                opp_ability_speed = opp_abilitydb['attackspeed']
            else:
                opp_slug_ability_name = None
                opp_slug_ability_damage = 0
            # endregion Opponent's Details
            # endregion
            # region Part 4 : Battle Calculations
            total_damage = slug_total_damage = slug_base_attack
            # total_damage = await self.battle_algo(
            #     char_attack, opp_defense, slug_base_attack, slug_ivattack, slug_evattack, slug_rank, slug_level
            # )
            opp_total_damage = opp_slug_total_damage = opp_slug_attack
            # endregion
            # region Part 5 : Ability Calculations
            ability_msg = ''

            ability_used = 0
            if abilitydb:
                # Unique Abilities
                ability_used, ability_msg = await self.ability_calc(
                    slug_name, slug_ability_no
                )

            if ability_used == 2:
                opp_shield, opp_health, total_damage = await self.ability_battle_calc(
                    slug_name, slug_ability_no,
                    opp_shield, slug_ability_damage, opp_health, total_damage
                )
                action_str = action_str + f"{slug_name.capitalize()}'s **{slug_ability_name.capitalize()}** {ability_msg} dealing {slug_ability_damage} damage\n"
                ability_used = 1

            # region Opponent's
            opp_ability_msg = ''
            opp_ability_used = 0
            if opp_abilitydb:
                # Unique Abilities
                opp_ability_used, opp_ability_msg = await self.ability_calc(
                    opp_slug_name, opp_slug_ability_no
                )

            if opp_ability_used == 2:
                shield, char_health, opp_total_damage = await self.ability_battle_calc(
                    opp_slug_name, opp_slug_ability_no,
                    shield, opp_slug_ability_damage, char_health, opp_total_damage
                )
                action_str += f"{opp_slug_name.capitalize()}'s **{opp_slug_ability_name.capitalize()}** {opp_ability_msg} dealing {opp_slug_ability_damage} damage\n"
                opp_ability_used = 1
            # endregion of Opponent's Ability
            # endregion
            # region Part 6 : Damage Calculations
            ran_accuracy = random.randint(1,120)
            ran_opp_accuracy = random.randint(1,120)

            if opp_slug_speed >= slug_speed:
                action_str += f"**{opp_name} used {opp_slug_name}**!\n"
                char_health, shield, action_str = await self.accuracy_check(
                    ran_opp_accuracy, opp_slug_accuracy, char_health, opp_total_damage, shield,
                    action_str, opp_name, opp_slug_name
                )
                action_str += f"**{char_name} used {slug_name}**!\n"
                opp_health, opp_shield, action_str = await self.accuracy_check(
                    ran_accuracy, slug_accuracy, opp_health, total_damage, opp_shield,
                    action_str, char_name, slug_name
                )
                # region Health Check : Case 1
                if char_health <= 0:
                    await self.you_lost_embed(ctx, char_name, opp_name, opp_imgurl, opp_slug_name)
                    break
                if opp_health <= 0:
                    await self.you_won_embed(
                        ctx, user_id, char_name, opp_name, slug_name, char_imgurl, gold_prize, gold,
                        slug1_id, slug1_exp, slug2_id, slug2_exp, slug3_id, slug3_exp, slug4_id, slug4_exp
                    )
                    win = 1
                    break
                # endregion
            else:  # if slug_speed > opp_slug_speed:
                action_str += f"**{char_name} used {slug_name}**!\n"
                opp_health, opp_shield, action_str = await self.accuracy_check(
                    ran_accuracy, slug_accuracy, opp_health, total_damage, opp_shield,
                    action_str, char_name, slug_name
                )
                action_str += f"**{opp_name} used {opp_slug_name}**!\n"
                char_health, shield, action_str = await self.accuracy_check(
                    ran_opp_accuracy, opp_slug_accuracy, char_health, opp_total_damage, shield,
                    action_str, opp_name, opp_slug_name
                )
                # region Health Check : Case 2
                if opp_health <= 0:
                    win = 1
                    await self.you_won_embed(
                        ctx, user_id, char_name, opp_name, slug_name, char_imgurl, gold_prize, gold,
                        slug1_id, slug1_exp, slug2_id, slug2_exp, slug3_id, slug3_exp, slug4_id, slug4_exp
                    )
                    break
                if char_health <= 0:
                    await self.you_lost_embed(ctx, char_name, opp_name, opp_imgurl, opp_slug_name)
                    break
                # endregion
                # region Previous Usages
                # if ran_accuracy < slug_accuracy:
                #     char_health = char_health - opp_total_damage
                # else:
                #     if shield <= 0:
                #         shield = 0
                #         char_health -= opp_total_damage
                #     else:
                #         shield -= opp_total_damage
                #         if shield < 0:
                #             shield = 0
                # if ran_opp_accuracy < opp_slug_accuracy:
                #     opp_health -= total_damage
                # else:
                #     if opp_shield <= 0:
                #         opp_shield = 0
                #         opp_health -= total_damage
                #     else:
                #         opp_shield -= total_damage
                #         if opp_shield < 0:
                #             opp_shield = 0

                # opp_health = opp_health - total_damage
                # char_health = char_health - opp_total_damage

                # await self.action_embed(ctx, char_name, slug_name, total_damage, opp_name, opp_slug_name,
                #                         opp_total_damage)

                # endregion

            # Action Embed after each command
            act_embed = discord.Embed(description=f"{action_str}", color=ctx.bot.main)
            await ctx.send(embed=act_embed)
            # endregion
            slug_data = await self.ability_after_attack(slug_data, slug_name, slug_ability_no, ch)
        return win

    @commands.command(aliases=['adv'])
    async def advance(self, ctx):
        user_id = int(ctx.message.author.id)
        await ctx.send("The BEGINNING of Advanced Battle Mode : Strato")

        # region User Database
        profiledb = await self.profiledb(user_id)
        start = profiledb[0]['start']
        if start == 0:
            start_embed = discord.Embed(
                title="Retry later",
                description="Please start your journey first using `.start`\nAny doubts? Ask at SlugShot support server",
                color=ctx.bot.invis
            )
            return await ctx.send(embed=start_embed)

        # Opponent Character Details
        opp_char = "Pronto"
        opp_slug1 = "rammstone"
        opp_slug2 = "infurnus"
        opp_slug3 = "frostcrawler"
        opp_slug4 = "flaringo"

        result = await self.battle(ctx, user_id,  opp_char, opp_slug1, opp_slug2, opp_slug3, opp_slug4)
        await ctx.send("The END of Advanced Battle Mode : Strato")

def setup(bot):
    bot.add_cog(Advanced_Battle_Modes(bot))
