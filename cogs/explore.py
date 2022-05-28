import discord
from discord.ext import commands
import random
import asyncio
import numpy as np

# from discord.ext.commands.cooldowns import BucketType

_mc = commands.MaxConcurrency(1, per=commands.BucketType.user, wait=False)
_cd = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)

data_list = [
    'a1', 'a2', 'a3', 'a4', 'a5',
    'b1', 'b2', 'b3', 'b4', 'b5',
    'c1', 'c2', 'c3', 'c4', 'c5',
    'd1', 'd2', 'd3', 'd4', 'd5',
    'e1', 'e2', 'e3', 'e4', 'e5',
]

regions = {
    "Wild Western Caverns": {
        "Shane Hideout": ["Kord Zane", "Pronto", "Trixie"],
        "Wild Spores Cavern": ["Pronto"],
        "Dark Spores Cavern": ["Pronto"],
        "Herringbone Cavern": ["Pronto"],
        "Rocklock Cavern": ["Kord Zane"],
    },
}
slugs = {
    "Shane Hideout": {
        "common": ['rammstone', 'hop rock'],
        "uncommon": ['armashelt', 'arachnet', ],
        "legendary": ['infurnus'],
    },
    "Wild Spores Cavern": {
        "common": ['flatulorhinkus'],
        "uncommon": ['flaringo'],
        "rare": ['bubbaleone'],
        "super rare": ['frostcrawler'],
        # "mythical": ['thugglet'],
    },
    "Dark Spores Cavern": {
        "common": ['flatulorhinkus'],
        "rare": ['speedstinger'],
        "super rare": ['grenuke', 'frightgeist'],
    },
    "Herringbone Cavern": {
        "uncommon": ['speedstinger'],
        "rare": ['grenuke', 'armashelt'],
    },
    "Rocklock Cavern": {
        "common": ['hop rock'],
        "uncommon": ['arachnet', 'rammstone'],
        "super rare": ['grenuke'],
    }
}
locations_no = {
    "Wild Western Caverns": {
        "Shane Hideout": 1,
        "Wild Spores Cavern": 2,
        "Dark Spores Cavern": 3,
        "Herringbone Cavern": 4,
        "Rocklock Cavern": 5,
    },
}


class Explore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def profiledb(self, user_id):
        profiledb = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        if not profiledb:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold, crystal, gem) VALUES ($1, $2, $3, $4)",
                                          user_id, 0, 0, 0)
        profiledb = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        return profiledb

    async def get_slugid(self, userid: int, slugid: str, total_slugno: int):
        slug_id = str(userid) + "#" + str(slugid) + "-" + str(total_slugno)
        return slug_id

    @commands.command(
        description="Shows your current location and region",
        aliases=['loc']
    )
    async def location(self, ctx):
        user_id = ctx.message.author.id
        profiledb = await self.profiledb(user_id)
        location = profiledb[0]['location']
        region = profiledb[0]['region']

        embed = discord.Embed(
            title="Current Location",
            description=f"**Location**: {location}\n**Region**: {region}",
            color=ctx.bot.main
        )
        embed.set_footer(text="Go to different locations using the .goto command")
        await ctx.send(embed=embed)

    @commands.command()
    async def slugloc(self, ctx):
        embed = discord.Embed(
            title="Slugs available at Locations",
            description="Region : Wild Western Caverns",
            color=ctx.bot.main
        )
        # for i in range(len(slugs)):
        #     embed.add_field(
        #         name = f"{slugs[0][region]}"
        #     )
        regions = list(slugs.keys())
        for k in range(len(regions)):
            str = ""
            region = regions[k]
            list_keys = list(slugs[region].keys())
            list_values = list(slugs[region].values())
            # print(region)
            for i in range(len(list_keys)):
                rarity = list_keys[i]
                str = str + "\n" + rarity + f" :\n"
                slugs_list = list_values[i]
                for j in range(len(slugs_list)):
                    # print("Slugs :",slugs_list[j])
                    str = str + f"{ctx.bot.tree} " + slugs_list[j] + "\n"
            embed.add_field(
                name=f"{region}",
                value=f"{str}",
                inline=True
            )
        embed.set_footer(text="You can travel to locations using .goto <loc> command")
        await ctx.send(embed=embed)

    @commands.command(
        description="Helps you move to a new location!",
        aliases=['gt']
    )
    async def goto(self, ctx, *, gotoloc):
        user_id = ctx.message.author.id
        profiledb = await self.profiledb(user_id)
        loc = profiledb[0]['location']
        region = profiledb[0]['region']
        current_coins = profiledb[0]['gold']

        current_loc_no = locations_no[region][loc]
        if region != "Wild Western Caverns":
            return await ctx.send("Invalid Region. Contact Support!")

        if gotoloc in locations_no[region]:
            pass
        else:
            return await ctx.send("Invalid location name!")

        new_loc_no = locations_no[region][gotoloc]
        cost = (abs(current_loc_no - new_loc_no)) * 50

        if (current_coins - cost) < 0:
            return await self.error_embed(ctx, "You don't have enough gold for that!")

        confirm_embed = discord.Embed(
            title="Confirm location",
            description=f"""
                        Are you sure you want to travel to {gotoloc} for {cost}?

                        ***Reply fast with reactions!***
                    """,
            color=ctx.bot.main
        )
        msg = await ctx.send(embed=confirm_embed)
        # endregion

        # region Timeout Embed
        timeout_embed = discord.Embed(
            title="Ah! You missed it!",
            color=ctx.bot.invis
        )
        # endregion

        # region Taking Input via reactions
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
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            return await msg.edit(embed=timeout_embed)
        else:
            pass
        # endregion

        if str(reaction.emoji) == tick:
            await self.bot.pg_con.execute("UPDATE profile SET location = $1 WHERE userid = $2", gotoloc, user_id)
            await self.bot.pg_con.execute("UPDATE profile SET gold = $1 WHERE userid = $2", current_coins - cost,
                                          user_id)
            end_embed = discord.Embed(title="Success",
                                      description=f"You have successfully traveled to {gotoloc} in {region}",
                                      color=ctx.bot.success)
            return await msg.edit(embed=end_embed)
        else:
            end_embed = discord.Embed(title="Cancelled", color=ctx.bot.invis)
            return await msg.edit(embed=end_embed)

        # if region == "Wild Western Caverns":
        #     if loc == "Shane Hideout":
        #         embed = discord.Embed(
        #             title = "Work in Progress",
        #             color = ctx.bot.main
        #         )
        #         await ctx.send(embed=embed)
        #     else:
        #         pass
        # else:
        #     pass

    async def error_embed(self, ctx, content):
        embed = discord.Embed(title="ERROR", description=f"{content}", color=ctx.bot.error)
        return await ctx.send(embed=embed)

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
        result_embed.set_author(name=f"{first_name} vs {second_name}")
        await ctx.send(embed=result_embed)

    # async def exp_reward(self, slug_id):
    #     slugdb = await self.bot.pg_con.fetch("SELECT * FROM allslugs WHERE slugid = $1", slug_id)
    #     user_exp = slugdb[0]['exp']
    #     random_exp = random.randint(30, 50)
    #     total_exp = user_exp + random_exp
    #     await self.bot.pg_con.execute(
    #         "UPDATE allslugs SET exp = $1 WHERE slugid = $2", total_exp, slug_id
    #     )

    # region EXPLORE BATTLE FUNCTIONS >>>
    async def character_data(self, char):
        health = int(char['health'])
        attack = int(char['attack'])
        defense = int(char['defense'])
        speed = char['speed']
        imgurl = char['imgurl']
        return health, attack, defense, speed, imgurl

    # async def battle_algo(self, char_attack, opp_defense, slug_attack, slug_ivattack, slug_evattack, slug_rank, slug_level):
    async def battle_algo(self, Attack, Defense, Base, IV, EV, Rank, Level):
        Base_Bonus = int((2 * Base + IV + (0.25 * EV)) * (1 / 2))
        Rank_Bonus = int((Base_Bonus * Rank * 0.01) + Rank / 2)
        Level_Bonus = int(((Base_Bonus * Level) / 50) + Level * 2)
        Rank_Level = int(Rank * Level * 0.05)

        Slug_Attack = int(Base_Bonus + Level_Bonus + Rank_Bonus + Rank_Level)
        Character_Bonus = int((Slug_Attack / 2 * (Attack / Defense) * 0.09))

        Total_Damage = Slug_Attack + Character_Bonus

        return Total_Damage
    # Base_Attack = int((2 * Base + IV + (0.25 * EV)) * (1 / 2))
    # Rank_Bonus = int( (Base * Rank * 0.01) + )
    # Slug_Attack = int(Base_Attack + (Base_Attack * Rank * 0.01) + Rank * 1.5)
    # Total_Damage = int(Slug_Attack + (Slug_Attack / 2 * (char_attack / opp_defense) * 0.09))

    # endregion <<< ABOVE

    async def explore_battle(self, ctx, user_id, opp_char, opp_slug1, opp_slug2, opp_slug3, opp_slug4):
        # user_id = int(ctx.message.author.id)
        # user = ctx.message.author
        # user_name = str(ctx.message.author.name)
        win = 0

        # region Profile Database
        profiledb = await self.profiledb(user_id)

        # Gold rewarded after match [Randomised]
        cgold = int(profiledb[0]['gold'])
        gold_prize = random.randint(10, 30)
        gold = cgold + gold_prize
        # endregion

        # region User's Character Details
        char_id = str(profiledb[0]['character'])
        char_type_id = (await self.bot.pg_con.fetchrow("SELECT * FROM allchars WHERE charid = $1",char_id))['chartypeid']
        char_name = (await self.bot.pg_con.fetchrow("SELECT * FROM chardata WHERE chartypeid = $1",char_type_id))['charname']
        chardb = await self.bot.pg_con.fetchrow("SELECT * FROM chardata WHERE charname = $1", char_name)
        char_health, char_attack, char_defense, char_speed, char_imgurl = await self.character_data(chardb)
        # endregion

        # region User's Slugs IDs and Emojis
        slug1_id = profiledb[0]['team1']
        slugemoji1 = await self.slug_emoji(slug1_id)
        slug2_id = profiledb[0]['team2']
        slugemoji2 = await self.slug_emoji(slug2_id)
        slug3_id = profiledb[0]['team3']
        slugemoji3 = await self.slug_emoji(slug3_id)
        slug4_id = profiledb[0]['team4']
        slugemoji4 = await self.slug_emoji(slug4_id)
        # endregion

        # region Opponent's Character Details
        # opp_characters = ['Kord Zane', 'Trixie', 'Pronto']
        opp_name = opp_char
        oppchardb = await self.bot.pg_con.fetchrow("SELECT * FROM chardata WHERE charname = $1", opp_name)
        opp_health, opp_attack, opp_defense, opp_speed, opp_imgurl = await self.character_data(oppchardb)
        # endregion

        # region Opponent's Slug Names and Emojis
        opp_slug1_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug1))[0][
            'slugemoji']
        opp_slug2_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug2))[0][
            'slugemoji']
        opp_slug3_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug3))[0][
            'slugemoji']
        opp_slug4_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug4))[0][
            'slugemoji']
        # endregion

        slug1_exp = slug2_exp = slug3_exp = slug4_exp = 0

        while True:
            # todo : to create an auto-editing embed that edits after every battle action [With reactions]
            # region Battle Embed
            battle_embed = discord.Embed(
                title=f"{char_name} VS {opp_name}",
                color=ctx.bot.main
            )
            battle_embed.add_field(
                name=f"{char_name}",
                value=f"Health : {char_health}\nSlugs : {slugemoji1}{slugemoji2}{slugemoji3}{slugemoji4}",
                inline=False
            )
            battle_embed.add_field(
                name=f"{opp_name}",
                value=f"Health : {opp_health}\nSlugs : {opp_slug1_emoji}{opp_slug2_emoji}{opp_slug3_emoji}{opp_slug4_emoji}",
                inline=False
            )
            battle_embed.set_footer(text="Choose your option : 1, 2, 3, 4 or 'ff'")
            bembed = await ctx.send(embed=battle_embed)

            # endregion

            # region Input for Action [Slug Choice]
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
            # endregion

            if slug_id == '' or slug_id is None:
                await ctx.send(f"There is no slug at position {choice}")
                continue

            # region User's Slug Details
            allslugsdb = await self.bot.pg_con.fetch("SELECT * FROM allslugs WHERE slugid = $1", slug_id)
            slug_name = allslugsdb[0]['slugname']
            slug_rank = allslugsdb[0]['rank']
            slug_level = allslugsdb[0]['level']
            slug_ivattack = allslugsdb[0]['iv_attack']
            slug_evattack = allslugsdb[0]['ev_attack']
            slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", slug_name)
            slug_attack = slugdatadb[0]['attack']
            slug_speed = slugdatadb[0]['speed']
            # endregion

            # region Opponent's Slug Details [Since bot, choices are random]
            opp_slug_name = random.choice([opp_slug1, opp_slug2, opp_slug3, opp_slug4])
            opp_slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug_name)
            opp_slug_rank = random.randint(1, 10)
            opp_slug_attack = opp_slugdatadb[0]['attack']
            opp_slug_speed = opp_slugdatadb[0]['speed']
            # endregion

            # region BATTLE Calculations for USER & OPPONENT
            # user
            # Base_Attack = int((2 * slug_attack + slug_ivattack + (0.25 * slug_evattack)) * (1 / 2))
            # Slug_Attack = int(Base_Attack + (Base_Attack * slug_rank * 0.01) + slug_rank * 1.5)
            # Total_Damage = int(Slug_Attack + (Slug_Attack / 2 * (char_attack / opp_defense) * 0.09))

            Total_Damage = await self.battle_algo(
                char_attack, opp_defense, slug_attack, slug_ivattack, slug_evattack, slug_rank, slug_level
            )

            # opponent
            opp_slug_damage = opp_slug_attack
            # endregion

            # region Damage Details [CHECK for Health]
            if opp_slug_speed > slug_speed:
                char_health = char_health - opp_slug_damage
                opp_health = opp_health - Total_Damage
                if char_health <= 0:
                    await self.you_lost_embed(ctx, char_name, opp_name, opp_imgurl, opp_slug_name)
                    break
                elif opp_health <= 0:
                    await self.you_won_embed(
                        ctx, user_id, char_name, opp_name, slug_name, char_imgurl, gold_prize, gold,
                        slug1_id, slug1_exp, slug2_id, slug2_exp, slug3_id, slug3_exp, slug4_id, slug4_exp
                    )
                    win = 1
                    break
                else:
                    await self.action_embed(ctx, opp_name, opp_slug_name, opp_slug_damage, char_name, slug_name,
                                            Total_Damage)

            elif slug_speed > opp_slug_speed:
                opp_health -= Total_Damage
                char_health = char_health - opp_slug_damage
                if opp_health <= 0:
                    win = 1
                    await self.you_won_embed(
                        ctx, user_id, char_name, opp_name, slug_name, char_imgurl, gold_prize, gold,
                        slug1_id, slug1_exp, slug2_id, slug2_exp, slug3_id, slug3_exp, slug4_id, slug4_exp
                    )
                    break
                elif char_health <= 0:
                    await self.you_lost_embed(ctx, char_name, opp_name, opp_imgurl, opp_slug_name)
                    break
                else:
                    await self.action_embed(ctx, char_name, slug_name, Total_Damage, opp_name, opp_slug_name,
                                            opp_slug_damage)

            else:  # when slug_speed == opp_slug_speed
                opp_health = opp_health - Total_Damage
                char_health = char_health - opp_slug_damage
                if opp_health <= 0:
                    await self.you_won_embed(
                        ctx, user_id, char_name, opp_name, slug_name, char_imgurl, gold_prize, gold,
                        slug1_id, slug1_exp, slug2_id, slug2_exp, slug3_id, slug3_exp, slug4_id, slug4_exp
                    )
                    # await self.exp_reward(slug_id)
                    win = 1
                    break
                elif char_health <= 0:
                    await self.you_lost_embed(ctx, char_name, opp_name, opp_imgurl, opp_slug_name)
                    break
                else:
                    await self.action_embed(ctx, char_name, slug_name, Total_Damage, opp_name, opp_slug_name,
                                            opp_slug_damage)
            # endregion
        return win
        # END of BATTLE BoT

    # async def char_slugs(self, char):
    #     if char == "Kord Zane":
    #         slugs = ['']
    #     else:
    #         slugs = ['tazerling', 'rammstone', 'armashelt']
    #     return slugs

    async def rarity_percent(self, rarities, ):
        percent = [0.44, 0.25, 0.15, 0.10, 0.05, 0.01]
        if "common" not in rarities:
            percent.remove(0.44)
        if "uncommon" not in rarities:
            percent.remove(0.25)
        if "rare" not in rarities:
            percent.remove(0.15)
        if "super rare" not in rarities:
            percent.remove(0.10)
        if "mythical" not in rarities:
            percent.remove(0.05)
        if "legendary" not in rarities:
            percent.remove(0.01)
        total_sum = 0
        for i in range(len(percent)):
            total_sum += percent[i]
        for i in range(len(percent)):
            percent[i] = round(percent[i] * (1 / total_sum), 2)
        check_sum = 0
        for i in range(len(percent)):
            check_sum += percent[i]
        # print(percent,check_sum)
        if check_sum > 1:
            percent[0] = round(percent[0] + (1 - check_sum), 2)
        if check_sum < 1:
            percent[0] = round(percent[0] - (1 - check_sum), 2)
        return percent

    # @commands.MaxConcurrency(1, per=commands.BucketType.user, wait=False)
    @commands.command(
        description="Explore the caverns, this and beyond!",
        aliases=['exp', 'x'],
        max_concurrency=_mc
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def explore(self, ctx):
        # embed = discord.Embed(title="Work in Progress",color=ctx.bot.invis)
        # return await ctx.send(embed=embed)
        user_id = ctx.message.author.id
        user_name = ctx.message.author.name

        # region Profile Database Details
        profiledb = await self.profiledb(user_id)
        start = profiledb[0]['start']
        if start == 0:
            start_embed = discord.Embed(title="Retry later",
                                        description="Please start your journey first using `.start`\nAny doubts? Ask at SlugShot support server",
                                        color=ctx.bot.invis)
            return await ctx.send(embed=start_embed)

        region = profiledb[0]['region']
        location = profiledb[0]['location']
        # endregion

        # region Opponent's Character's List

        try:
            opp_chars = regions[region][location]
        except KeyError:
            return await self.error_embed(ctx, "This Cavern is Locked")
        # endregion

        opp_char = random.choice(opp_chars)
        oppchardb = await self.bot.pg_con.fetch("SELECT * FROM chardata WHERE charname = $1", opp_char)
        opp_slug1 = oppchardb[0]['slug1']
        opp_slug2 = oppchardb[0]['slug2']
        opp_slug3 = oppchardb[0]['slug3']
        opp_slug4 = oppchardb[0]['slug4']
        win = await self.explore_battle(ctx, user_id, opp_char, opp_slug1, opp_slug2, opp_slug3, opp_slug4)

        # region After Battle,
        chance = random.randint(1, 100)
        # print(chance)
        if win == 1:
            if chance > 80:
                pass
            else:
                return
        else:
            return

        # region Chance Embed
        chance_embed = discord.Embed(
            title="New Slug Found",
            description=f"""
                A slug {ctx.bot.question_mark} wants to join your team!
                Do you want to catch it or not?
                
                ***Reply fast with reactions!***
            """,
            color=ctx.bot.main
        )
        chance_embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/716625655692787801/976451381655379998/Unclassified.webp")
        cembed = msg = await ctx.send(embed=chance_embed)
        # endregion

        # region Timeout Embed
        timeout_embed = discord.Embed(
            title="Ah! You missed it!",
            color=ctx.bot.invis
        )
        # endregion

        # region Taking Input via reactions
        tick = "\U00002611"
        cross = "\U0000274e"
        await cembed.add_reaction(tick)
        await cembed.add_reaction(cross)

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
            rarities = list(slugs[location].keys())
            percent = await self.rarity_percent(rarities)
            # print(percent)

            slug_rarity = np.random.choice(a=rarities, p=percent)
            slug_name = random.choice(slugs[location][slug_rarity])

            # region Database Changes
            team1 = profiledb[0]['team1']
            team2 = profiledb[0]['team2']
            team3 = profiledb[0]['team3']
            team4 = profiledb[0]['team4']

            slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", str(slug_name))

            img = slugdatadb[0]['protoimgurl']
            slugtypeid = slugdatadb[0]['slugtypeid']
            total_slugs = profiledb[0]['total_slugs'] + 1
            slugid = await self.get_slugid(user_id, slugtypeid, total_slugs)

            iv_attack = random.randint(70, 100)
            con_pos = None
            container_pos = None
            if team1 is None:
                team_pos = 1
                await self.bot.pg_con.execute("UPDATE profile SET team1 = $1 WHERE userid = $2", slugid, user_id)
            elif team2 is None:
                team_pos = 2
                await self.bot.pg_con.execute("UPDATE profile SET team2 = $1 WHERE userid = $2", slugid, user_id)
            elif team3 is None:
                team_pos = 3
                await self.bot.pg_con.execute("UPDATE profile SET team3 = $1 WHERE userid = $2", slugid, user_id)
            elif team4 is None:
                team_pos = 4
                await self.bot.pg_con.execute("UPDATE profile SET team4 = $1 WHERE userid = $2", slugid, user_id)
            else:
                team_pos = 0

                con_pos = 0
                for i in range(1, 2):  # container
                    for j in range(len(data_list)):  # inside a container
                        container_pos = str(i) + '-' + str(data_list[j])
                        containerdb = await self.bot.pg_con.fetch(
                            "SELECT * FROM allslugs WHERE container_position = $1 and userid = $2",
                            container_pos, user_id)
                        try:
                            new_slugid = containerdb[0]['slugid']
                        except IndexError:
                            con_pos = container_pos
                            break
                        else:
                            pass
                    if con_pos != 0:
                        break

            await self.bot.pg_con.execute(
                "INSERT INTO allslugs (slugid, slugtypeid, userid, slugname, iv_attack, team_position, container_position) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                str(slugid), str(slugtypeid), int(user_id), str(slug_name), int(iv_attack), str(team_pos),
                str(container_pos)
            )
            await self.bot.pg_con.execute(
                "UPDATE profile SET total_slugs = $1 WHERE userid = $2", total_slugs, user_id
            )
            # endregion
            changes_embed = discord.Embed(
                title="Congrats! New Slug Caught",
                description=f"{slug_name} added to your team!",
                color=ctx.bot.main
            )
            changes_embed.set_thumbnail(url=img)
            await cembed.edit(embed=changes_embed)

        if str(reaction.emoji) == cross:
            await cembed.edit("You scared away that slug!")
        # End of EXPLORE

    @commands.command()
    async def generate(self, ctx):
        user_id = int(ctx.message.author.id)

    @commands.command(max_concurrency=_mc)
    async def start(self, ctx):
        user_id = int(ctx.message.author.id)

        # region Profile Database
        profiledb = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        if not profiledb:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold, crystal, gem) VALUES ($1, $2, $3, $4)",
                                          user_id, 0, 0, 0)
        profiledb = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        team1 = profiledb[0]['team1']
        team2 = profiledb[0]['team2']
        team3 = profiledb[0]['team3']
        team4 = profiledb[0]['team4']
        # endregion
        current_start = int(profiledb[0]['start'])
        if current_start == 1:
            return await ctx.send("You have already started your journey. If you want help, join the support server!")

        # region Step 1 : Choosing a Slug
        thumbnail = "https://cdn.discordapp.com/attachments/972907787606712390/975835488747409468/1652727699337.png"
        embed1 = discord.Embed(
            title="Welcome to SlugShot Arena",
            description="SlugShot is a Fan made Slugterra based Discord Game Bot that will provide you the best slugterra experience you can ever find. Battle, Trade and Explore the deep caverns!",
            color=ctx.bot.main
        )
        embed1.add_field(
            name="STEP 1 : Choose your starter slug",
            value=f"""
            1) {ctx.bot.fire} Flaringo
            2) {ctx.bot.water} Aquabeek
            3) {ctx.bot.earth} Rammstone
            4) {ctx.bot.electric} Tazerling 
            5) {ctx.bot.air} Flatulorhinkus
            """,
        )
        embed1.set_thumbnail(url=thumbnail)
        # embed1.set_author(name=self.bot.name,icon_url=self.bot.avatar_url)
        embed_step1 = await ctx.send(embed=embed1, content=None)


        def check(a):
            return a.author == ctx.message.author and (
                    a.content == "1" or a.content == "2" or a.content == "3" or a.content == "4" or a.content == "5")

        msg = await self.bot.wait_for('message', check=check)
        choice = int(msg.content)

        if choice == 1:
            slug_name = "flaringo"
        elif choice == 2:
            slug_name = "aquabeek"
        elif choice == 3:
            slug_name = "rammstone"
        elif choice == 4:
            slug_name = "tazerling"
        elif choice == 5:
            slug_name = "flatulorhinkus"
        else:
            return await ctx.send("Choose a number. Retry later.")

        slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", str(slug_name))

        slugtypeid = slugdatadb[0]['slugtypeid']
        total_slugs = profiledb[0]['total_slugs'] + 1
        slugid = await self.get_slugid(user_id, slugtypeid, total_slugs)

        iv_attack = random.randint(70, 100)
        container_pos = None
        con_pos = None
        if team1 is None:
            team_pos = 1
            await self.bot.pg_con.execute("UPDATE profile SET team1 = $1 WHERE userid = $2", slugid, user_id)
        elif team2 is None:
            team_pos = 2
            await self.bot.pg_con.execute("UPDATE profile SET team2 = $1 WHERE userid = $2", slugid, user_id)
        elif team3 is None:
            team_pos = 3
            await self.bot.pg_con.execute("UPDATE profile SET team3 = $1 WHERE userid = $2", slugid, user_id)
        elif team4 is None:
            team_pos = 4
            await self.bot.pg_con.execute("UPDATE profile SET team4 = $1 WHERE userid = $2", slugid, user_id)
        else:
            team_pos = 0
            data_list = [
                'a1', 'a2', 'a3', 'a4', 'a5',
                'b1', 'b2', 'b3', 'b4', 'b5',
                'c1', 'c2', 'c3', 'c4', 'c5',
            ]
            con_pos = 0
            for i in range(1, 2):  # container
                for j in range(len(data_list)):  # inside a container
                    container_pos = str(i) + '-' + str(data_list[j])
                    containerdb = await self.bot.pg_con.fetch("SELECT * FROM allslugs WHERE container_position = $1",
                                                              container_pos)
                    try:
                        new_slugid = containerdb[0]['slugid']
                    except IndexError:
                        con_pos = container_pos
                        break
                    else:
                        pass
                    # print(slugid is None)
                    # print(containerdb is None)
                    # print(containerdb == '')
                    # print(containerdb == '[]')
                    # if containerdb == "[]" or containerdb is None:
                if con_pos != 0:
                    break
        # print(container_pos, con_pos)
        await self.bot.pg_con.execute(
            "INSERT INTO allslugs (slugid, slugtypeid, userid, slugname, iv_attack, team_position, container_position) VALUES ($1, $2, $3, $4, $5, $6, $7)",
            str(slugid), str(slugtypeid), int(user_id), str(slug_name), int(iv_attack), str(team_pos),
            str(container_pos)
        )
        await self.bot.pg_con.execute(
            "UPDATE profile SET total_slugs = $1 WHERE userid = $2", total_slugs, user_id
        )
        # await ctx.send("Done. Rule the Arena!")

        embed2 = discord.Embed(
            title="Step 1 Done",
            description=f"""
                    You chose {slug_name.capitalize()} as your starter slug!
                    Know about the slug's stats through `.team 1`
                    """,
            color=ctx.bot.invis
        )
        # embed2.set_author(name=self.bot.name, icon_url=self.bot.avatar_url)
        embed2.set_footer(text="You can earn more slugs through exploring the caverns!")
        await embed_step1.edit(embed=embed2)

        #endregion

        #region Step 2 : Getting Characters
        char_embed = discord.Embed(
            title = "Step 2 : Characters in SlugShot",
            description = """
            There are many characters in SlugShot. From SlugSlingers, Fighters, to Special Characters, all have different stats and unique abilities. So, unlock them and use them in battles.""",
            color = ctx.bot.main
        )
        char2_embed = discord.Embed(
            description="As your first character, I give you the first character, Young Eli, you have unlocked Young ELI!",
            color=ctx.bot.main
        )
        char2_embed.set_author(name = "Master SlugShot")

        await ctx.send(embed=char_embed)
        await ctx.send(embed=char2_embed)

        # region STEP 3 : Battle/Duel
        embed3 = discord.Embed(
            title="Step 3 : Battle/Duel",
            description="SlugShot offers a smooth battle experience with a text to text battle! The AI behind Battle Algorithm is designed to provide epic battles!",
            color=ctx.bot.main
        )
        embed3.add_field(
            name="Basics of Dueling :",
            value=f"""
                ▫️ **Understand your Slug**
                They are more than just ammo!

                ▫️ **Every Slug has its own unique abilities**
                Even Flopper's! 😜

                ▫️ **Play Smart!**
                Strategy is Key!

                ▫️ **Always follow the SlugSlinger's Code**
                Check it out by typing `.slugcode`

                ***Now, It's time for a DUEL !***
            """,
        )
        embed3.set_thumbnail(url=thumbnail)
        # embed3.set_author(name=self.bot.user.name, icon_url=self.bot.avatar_url)
        embed_step2 = await ctx.send(embed=embed3, content=None)
        await asyncio.sleep(5)

        embed_step2_battle = discord.Embed(
            title="Duel Challenge!",
            description="Champion of SlugShot Arena has challenged you!",
            color=ctx.bot.main
        )
        embed_step2_battle.set_footer(text="Do you accept or not? `accept` or `decline`")
        embed_step2_battle.set_author(name="Champion SlugShot")

        # Battle Command HERE
        await self.explore_battle(ctx, user_id, "Eli Shane", "infurnus", "aquabeek", "frostcrawler", "arachnet")
        await ctx.send("Battle command under construction")

        embed_step3 = discord.Embed(
            title="Good Game!",
            description="You gave your best but now its time to improve your team overall!",
            color=ctx.bot.main
        )
        embed_step3.add_field(
            name="Tips & Tricks :",
            value=f"""
            - Level up your slugs
            - Get more skilled characters in your team!
            """,
            inline=False
        )
        await ctx.send(embed=embed_step3)

        finish_embed = discord.Embed(
            title="Tutorial Finished.",
            description="You're on your own now. Your journey has been started.",
            colour=ctx.bot.main
        )
        finish_embed.set_author(
            name="SlugShot",
            icon_url=self.bot.user.avatar_url
        )
        finish_embed.set_footer(
            text="Any doubts, Join the Support Server or Explore."
        )
        await ctx.send(embed=finish_embed)
        await self.bot.pg_con.execute("UPDATE profile SET start = $1 WHERE userid = $2", 1, user_id)


def setup(bot):
    bot.add_cog(Explore(bot))
