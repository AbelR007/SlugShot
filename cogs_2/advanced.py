import discord
import random
import asyncio
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType

_mc = commands.MaxConcurrency(1, per=commands.BucketType.user, wait=False)
_cd = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)


regions = {
    "Wild Western Caverns": {
        "Shane Hideout": ["Kord Zane", "Pronto", "Trixie"],
        "Wild Spores Cavern": ["Pronto"],
        "Dark Spores Cavern": ["Pronto","Trixie"],
        "Herringbone Cavern": ["Pronto"],
        "Rocklock Cavern": ["Kord Zane"],
    },
}
# slugs = {
#     "Shane Hideout": {
#         "common": ['rammstone', 'hop rock'],
#         "uncommon": ['armashelt', 'arachnet', ],
#         "legendary": ['infurnus'],
#     },
#     "Wild Spores Cavern": {
#         "common": ['flatulorhinkus'],
#         "uncommon": ['flaringo'],
#         "rare": ['bubbaleone'],
#         "super rare": ['frostcrawler'],
#         # "mythical": ['thugglet'],
#     },
#     "Dark Spores Cavern": {
#         "common": ['flatulorhinkus'],
#         "rare": ['speedstinger'],
#         "super rare": ['grenuke', 'frightgeist'],
#     },
#     "Herringbone Cavern": {
#         "uncommon": ['speedstinger'],
#         "rare": ['grenuke', 'armashelt'],
#     },
#     "Rocklock Cavern": {
#         "common": ['hop rock'],
#         "uncommon": ['arachnet', 'rammstone'],
#         "super rare": ['grenuke'],
#     }
# }
# locations_no = {
#     "Wild Western Caverns": {
#         "Shane Hideout": 1,
#         "Wild Spores Cavern": 2,
#         "Dark Spores Cavern": 3,
#         "Herringbone Cavern": 4,
#         "Rocklock Cavern": 5,
#     },
# }


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

    async def slugdata_fromdb(self, slug_id, stat):
        allslugs = await self.bot.pg_con.fetchrow("SELECT * FROM allslugs WHERE slugid = $1",slug_id)
        statdata = allslugs[f'{stat}']
        return statdata

    async def chardata_fromdb(self, char_name, stat):
        chardb = await self.bot.pg_con.fetchrow("SELECT * FROM chardata WHERE charname = $1", char_name)
        statdata = chardb[f'{stat}']
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

    async def stat_algo(self, Base, IV, EV, Rank, Level):
        Base_Bonus = int((2*Base + IV + (0.25 * EV)) * 0.3)
        return Base_Bonus

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
                # endregion Flash Fire
        else:
            pass
        return opp_shield, opp_health, slug_total_damage

    async def ability_before_battle(self, slug_data, char_health):
        for i in range(1,4+1):
            slug_name = slug_data[f'slug{i}_name']
            slug_ability_no = slug_data[f'slug{i}_ability_no']

            slug_base_attack = slug_data[f'slug{i}_base_attack']

            if slug_ability_no == 2:
                char_health = int(char_health - (char_health * (5/100)))

            if slug_name == 'infurnus':
                if slug_ability_no == 2:
                    slug_ability_damage = 80
                    slug_base_attack -= int(slug_ability_damage - slug_ability_damage / 3)
                    slug_data[f'slug{i}_base_attack'] = slug_base_attack

            elif slug_name == 'rammstone':
                if slug_ability_no == 2:
                    slug_base_attack -= 20
                    slug_data[f'slug{i}_base_attack'] = slug_base_attack
            else:
                pass
        return slug_data, char_health

    async def ability_after_attack(self, slug_data, char_health, shield, ch, opp_slugdata, opp_health, opp_shield, och, slug_name, slug_ability_no, action_str):
        current_damage = slug_data[f'slug{ch}_base_attack']
        if slug_name == "rammstone":
            if slug_ability_no == 2:
                # region Battle Up
                current_damage = current_damage + current_damage*(10/100)
                slug_data[f'slug{ch}_base_attack'] = int(current_damage)
                action_str += "Rammstone's **Battleup** increased the slug's damage!\n"
                # endregion

        elif slug_name == 'arachnet':
            if slug_ability_no == 2:
                # region Flashnet
                opp_slugdata[f'slug{och}_base_speed'] -= int((opp_slugdata[f'slug{och}_base_speed'])*(10/100))
                action_str += "Arachnet's **Flashnet** decreased the opposing slug's speedn\n"
                # endregion

        elif slug_name == 'frostcrawler':
            if slug_ability_no == 2:
                # region Glaciator
                shield += 70
                # endregion

        elif slug_name == 'boon doc':
            if slug_ability_no == 2:
                # region Medici
                char_health += 100
                # endregion

        elif slug_name == 'armashelt':
            if slug_ability_no == 2:
                # region
                slug_data[f'slug{ch}_accuracy'] += int(slug_data[f'slug{ch}_accuracy']*(7/100))
                # endregion

        else:
            pass
        # Changes
        return slug_data, opp_slugdata, shield, opp_shield, char_health, opp_health, action_str
    # endregion

    async def battle(self, ctx, user_id, opp_char, opp_slug1, opp_slug2, opp_slug3, opp_slug4):
        profiledb = await self.profiledb(user_id)
        current_gold = int(profiledb[0]['gold'])
        gold_prize = random.randint(10,20)
        gold = gold_prize + current_gold

        # region User :  Character Details
        char_id = str(profiledb[0]['character'])
        char_type_id = (await self.bot.pg_con.fetchrow("SELECT * FROM allchars WHERE charid = $1", char_id))[
            'chartypeid']
        char_name = (await self.bot.pg_con.fetchrow("SELECT * FROM chardata WHERE chartypeid = $1", char_type_id))[
            'charname']
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

            'slug1_rank': await self.slugdata_fromdb(slug1_id, 'rank'),
            'slug2_rank': await self.slugdata_fromdb(slug2_id, 'rank'),
            'slug3_rank': await self.slugdata_fromdb(slug3_id, 'rank'),
            'slug4_rank': await self.slugdata_fromdb(slug4_id, 'rank'),

            'slug1_level': await self.slugdata_fromdb(slug1_id, 'level'),
            'slug2_level': await self.slugdata_fromdb(slug2_id, 'level'),
            'slug3_level': await self.slugdata_fromdb(slug3_id, 'level'),
            'slug4_level': await self.slugdata_fromdb(slug4_id, 'level'),

            'slug1_base_health': await self.slugdata_specific(slug1_name, 'health'),
            'slug1_base_attack': await self.slugdata_specific(slug1_name, 'attack'),
            'slug1_base_defense': await self.slugdata_specific(slug1_name, 'defense'),
            'slug1_base_speed': await self.slugdata_specific(slug1_name, 'speed'),
            'slug1_base_accuracy': await self.slugdata_specific(slug1_name, 'accuracy'),
            'slug1_base_retrieval': await self.slugdata_specific(slug1_name, 'retrieval'),

            'slug2_base_health': await self.slugdata_specific(slug2_name, 'health'),
            'slug2_base_attack': await self.slugdata_specific(slug2_name, 'attack'),
            'slug2_base_defense': await self.slugdata_specific(slug2_name, 'defense'),
            'slug2_base_speed': await self.slugdata_specific(slug2_name, 'speed'),
            'slug2_base_accuracy': await self.slugdata_specific(slug2_name, 'accuracy'),
            'slug2_base_retrieval': await self.slugdata_specific(slug2_name, 'retrieval'),

            'slug3_base_health': await self.slugdata_specific(slug3_name, 'health'),
            'slug3_base_attack': await self.slugdata_specific(slug3_name, 'attack'),
            'slug3_base_defense': await self.slugdata_specific(slug3_name, 'defense'),
            'slug3_base_speed': await self.slugdata_specific(slug3_name, 'speed'),
            'slug3_base_accuracy': await self.slugdata_specific(slug3_name, 'accuracy'),
            'slug3_base_retrieval': await self.slugdata_specific(slug3_name, 'retrieval'),

            'slug4_base_health': await self.slugdata_specific(slug4_name, 'health'),
            'slug4_base_attack': await self.slugdata_specific(slug4_name, 'attack'),
            'slug4_base_defense': await self.slugdata_specific(slug4_name, 'defense'),
            'slug4_base_speed': await self.slugdata_specific(slug4_name, 'speed'),
            'slug4_base_accuracy': await self.slugdata_specific(slug4_name, 'accuracy'),
            'slug4_base_retrieval': await self.slugdata_specific(slug4_name, 'retrieval'),

            'slug1_ability_no': await self.slugdata_fromdb(slug1_id, 'abilityno'),
            'slug2_ability_no': await self.slugdata_fromdb(slug2_id, 'abilityno'),
            'slug3_ability_no': await self.slugdata_fromdb(slug3_id, 'abilityno'),
            'slug4_ability_no': await self.slugdata_fromdb(slug4_id, 'abilityno'),

            'char_health': await self.chardata_fromdb(char_name, 'health'),
        }
        # region Stat Updates
        char_health = slug_data['char_health']
        stats = ['health','attack','defense','speed','accuracy','retrieval']
        for i in range(1,4+1):
            for stat in stats:
                if i == 1:
                    slug_data[f'slug{i}_iv_{stat}'] = await self.slugdata_fromdb(slug1_id, f'iv_{stat}')
                if i == 2:
                    slug_data[f'slug{i}_iv_{stat}'] = await self.slugdata_fromdb(slug2_id, f'iv_{stat}')
                if i == 3:
                    slug_data[f'slug{i}_iv_{stat}'] = await self.slugdata_fromdb(slug3_id, f'iv_{stat}')
                if i == 4:
                    slug_data[f'slug{i}_iv_{stat}'] = await self.slugdata_fromdb(slug4_id, f'iv_{stat}')
        for i in range(1,4+1):
            for stat in stats:
                base_stat = slug_data[f'slug{i}_base_{stat}']
                iv_stat = slug_data[f'slug{i}_iv_{stat}']
                ev_stat = 1
                rank = slug_data[f'slug{i}_rank']
                level = slug_data[f'slug{i}_level']
                slug_data[f'slug{i}_{stat}'] = await self.stat_algo(base_stat, iv_stat, ev_stat, rank, level)
        # endregion
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
        opp_slugdata = {
            'slug1_name': opp_slug1,
            'slug2_name': opp_slug2,
            'slug3_name': opp_slug3,
            'slug4_name': opp_slug4,

            'slug1_base_health': await self.slugdata_specific(opp_slug1, 'health'),
            'slug2_base_health': await self.slugdata_specific(opp_slug2, 'health'),
            'slug3_base_health': await self.slugdata_specific(opp_slug3, 'health'),
            'slug4_base_health': await self.slugdata_specific(opp_slug4, 'health'),

            'slug1_base_attack': await self.slugdata_specific(opp_slug1, 'attack'),
            'slug2_base_attack': await self.slugdata_specific(opp_slug2, 'attack'),
            'slug3_base_attack': await self.slugdata_specific(opp_slug3, 'attack'),
            'slug4_base_attack': await self.slugdata_specific(opp_slug4, 'attack'),

            'slug1_base_defense': await self.slugdata_specific(opp_slug1, 'defense'),
            'slug2_base_defense': await self.slugdata_specific(opp_slug2, 'defense'),
            'slug3_base_defense': await self.slugdata_specific(opp_slug3, 'defense'),
            'slug4_base_defense': await self.slugdata_specific(opp_slug4, 'defense'),

            'slug1_base_speed': await self.slugdata_specific(opp_slug1, 'speed'),
            'slug2_base_speed': await self.slugdata_specific(opp_slug2, 'speed'),
            'slug3_base_speed': await self.slugdata_specific(opp_slug3, 'speed'),
            'slug4_base_speed': await self.slugdata_specific(opp_slug4, 'speed'),

            'slug1_base_accuracy': await self.slugdata_specific(opp_slug1, 'accuracy'),
            'slug2_base_accuracy': await self.slugdata_specific(opp_slug2, 'accuracy'),
            'slug3_base_accuracy': await self.slugdata_specific(opp_slug3, 'accuracy'),
            'slug4_base_accuracy': await self.slugdata_specific(opp_slug4, 'accuracy'),

            'slug1_base_retrieval': await self.slugdata_specific(opp_slug1, 'retrieval'),
            'slug2_base_retrieval': await self.slugdata_specific(opp_slug2, 'retrieval'),
            'slug3_base_retrieval': await self.slugdata_specific(opp_slug3, 'retrieval'),
            'slug4_base_retrieval': await self.slugdata_specific(opp_slug4, 'retrieval'),

            'slug1_ability_no': random.randint(1,2),  # await self.slugdata_fromdb(slug1_id, 'abilityno'),
            'slug2_ability_no': random.randint(1,2),  # await self.slugdata_fromdb(slug2_id, 'abilityno'),
            'slug3_ability_no': random.randint(1,2),  # await self.slugdata_fromdb(slug3_id, 'abilityno'),
            'slug4_ability_no': random.randint(1,2),  # await self.slugdata_fromdb(slug4_id, 'abilityno'),
        }
        opp_slug_level = random.randint(1, 5)  # 1 - 10
        opp_slug_rank = random.randint(1, 25)  # 1 - 50
        opp_slug_ivattack = random.randint(1, 50)  # 1 - 100
        opp_slug_evattack = random.randint(1, 100)  # 1 - 100
        # region >>> Shield >>>
        shield = slug1_health + slug2_health + slug3_health + slug4_health
        opp_shield = opp_slug1_health + opp_slug2_health + opp_slug3_health + opp_slug4_health
        # endregion

        slug1_exp = slug2_exp = slug3_exp = slug4_exp = 0
        win = 0

        slug_data, char_health = await self.ability_before_battle(slug_data, char_health)
        opp_slugdata, opp_health = await self.ability_before_battle(opp_slugdata, opp_health)
        while True:
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

            slug_base_health = slug_data[f'slug{ch}_base_health']
            slug_base_attack = slug_data[f'slug{ch}_base_attack']  # slugdata['attack']
            slug_base_defense = slugdata['defense']
            slug_base_speed = slug_data[f'slug{ch}_base_speed']
            slug_base_accuracy = slug_data[f'slug{ch}_base_accuracy']
            slug_base_retrieval = slug_data[f'slug{ch}_base_retrieval']

            slug_ivhealth = allslugsdb['iv_health']
            slug_ivattack = allslugsdb['iv_attack']
            slug_ivdefense = allslugsdb['iv_defense']
            slug_ivspeed = allslugsdb['iv_speed']
            slug_ivaccuracy = allslugsdb['iv_accuracy']
            slug_ivretrieval = allslugsdb['iv_retrieval']

            slug_evhealth = allslugsdb['ev_health']
            slug_evattack = allslugsdb['ev_attack']
            slug_evdefense = allslugsdb['ev_defense']
            slug_evspeed = allslugsdb['ev_speed']
            slug_evaccuracy = allslugsdb['ev_accuracy']
            slug_evretrieval = allslugsdb['ev_retrieval']

            slug_ability_no = slug_data[f'slug{ch}_ability_no']  # allslugsdb['abilityno']

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
            och = random.randint(1,4)
            # och = 4
            if och == 1:
                opp_slug_name = opp_slug1
            elif och == 2:
                opp_slug_name = opp_slug2
            elif och == 3:
                opp_slug_name = opp_slug3
            else:
                opp_slug_name = opp_slug4
            opp_slugdb = await self.bot.pg_con.fetchrow("SELECT * FROM slugdata WHERE slugname = $1", opp_slug_name)

            opp_slug_base_health = opp_slugdb['health']
            opp_slug_attack = opp_slugdata[f'slug{och}_base_attack']  # opp_slugdb['attack']
            opp_slug_defense = opp_slugdb['defense']
            opp_slug_speed = opp_slugdata[f'slug{och}_base_speed']
            opp_slug_accuracy = opp_slugdb['accuracy']


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

            # total_damage = slug_total_damage = slug_base_attack
            total_damage = await self.battle_algo(
                char_attack, opp_defense, slug_base_attack, slug_ivattack, slug_evattack, slug_rank, slug_level
            )
            # slug_speed = await self.stat_algo(
            #     slug_base_speed, slug_ivspeed, slug_evspeed, slug_rank, slug_level
            # )
            slug_speed = slug_data[f'slug{ch}_speed']
            slug_accuracy = slug_data[f'slug{ch}_accuracy']

            # opp_total_damage  = opp_slug_total_damage = opp_slug_attack
            opp_total_damage = await self.battle_algo(
                opp_attack, char_defense, opp_slug_attack, opp_slug_ivattack, opp_slug_evattack, opp_slug_rank, opp_slug_level
            )
            # opp_slug_speed = await self.stat_algo

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
            # region Part 5.2 : Ability Calculations

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
            # endregion
            slug_data, opp_slugdata, shield, opp_shield, char_health, opp_health, action_str = await self.ability_after_attack(
                slug_data, char_health, shield, ch, opp_slugdata, opp_health, opp_shield, och, slug_name, slug_ability_no, action_str
            )
            opp_slugdata, slug_data, opp_shield, shield, opp_health, char_health, action_str = await self.ability_after_attack(
                opp_slugdata, opp_health, opp_shield, och, slug_data, char_health, shield, ch, opp_slug_name, opp_slug_ability_no, action_str
            )
            act_embed = discord.Embed(description=f"{action_str}", color=ctx.bot.main)
            await ctx.send(embed=act_embed)
        return win

    # @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @commands.command(
        description="Explore the caverns, this and beyond!",
        aliases=['exp', 'x'],
        max_concurrency=_mc
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def explore(self, ctx):
        user_id = int(ctx.message.author.id)
        await ctx.send("The BEGINNING of Advanced Battle Mode : Strato")
        print("Hmm")

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

        # region Opponent's Character's List

        try:
            opp_chars = regions[region][location]
        except KeyError:
            return await self.error_embed(ctx, "This Cavern is Locked")
        # endregion

        # region Opponent's Slugs's List
        opp_char = random.choice(opp_chars)
        oppchardb = await self.bot.pg_con.fetch("SELECT * FROM chardata WHERE charname = $1", opp_char)
        opp_slug1 = oppchardb[0]['slug1']
        opp_slug2 = oppchardb[0]['slug2']
        opp_slug3 = oppchardb[0]['slug3']
        opp_slug4 = oppchardb[0]['slug4']

        result = await self.battle(ctx, user_id,  opp_char, opp_slug1, opp_slug2, opp_slug3, opp_slug4)
        # await ctx.send("The END of Advanced Battle Mode : Strato")

        # region After Battle,
        chance = random.randint(1, 100)
        # print(chance)
        if result == 1:
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


async def setup(bot):
    await bot.add_cog(Advanced_Battle_Modes(bot))
