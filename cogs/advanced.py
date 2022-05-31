import discord
from discord.ext import commands, tasks

class Advanced_Battle_Modes(commands.Cog):
    def __init(self, bot):
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

    # endregion

    async def battle(self, ctx, user_id, opp_char, opp_slug1, opp_slug2, opp_slug3, opp_slug4):
        profiledb = await self.profiledb(user_id)
        current_gold = int(profiledb[0]['gold'])

        # region User :  Character Details
        char_name = "Young Eli"
        chardb = await self.bot.pg_con.fetchrow("SELECT * FROM chardata WHERE charname = $1", char_name)
        char_health, char_attack, char_defense, char_speed, char_imgurl = await self.character_data(chardb)

        # Slug IDs & Emojis for Battle Card
        slug1_id = profiledb[0]['team1']
        slugemoji1 = await self.slug_emoji(slug1_id)
        slug2_id = profiledb[0]['team2']
        slugemoji2 = await self.slug_emoji(slug2_id)
        slug3_id = profiledb[0]['team3']
        slugemoji3 = await self.slug_emoji(slug3_id)
        slug4_id = profiledb[0]['team4']
        slugemoji4 = await self.slug_emoji(slug4_id)
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
        # endregion

        slug1_exp = slug2_exp = slug3_exp = slug4_exp = 0
        win = 0
        while True:
            # region Part 1 : Battle Embed
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

            if slug_id == '' or slug_id is None:
                await ctx.send(f"There is no slug at position {choice}")
                continue
            # endregion
            # region Part 3 : User & Opponent's Slug Details
            allslugsdb = await self.bot.pg_con.fetchrow("SELECT * FROM allslugs WHERE slugid = $1", slug_id)
            slug_name  = allslugsdb['slugname']
            slugdata = await self.bot.pg_con.fetchrow("SELECT * FROM slugdata WHERE slugname = $1", slug_name)

            slug_level = allslugsdb['level']
            slug_rank = allslugsdb['rank']

            health = slugdata['health']
            attack = slugdata['attack']
            defense = slugdata['defense']
            speed = slugdata['speed']
            attack_speed = slugdata['attackspeed']
            accuracy = slugdata['accuracy']

            # Opponent's Choice of Slug
            opp_slug_name = random.choice([opp_slug1,opp_slug2,opp_slug3,opp_slug4])
            opp_slugdata = await self.bot.pg_con.fetchrow("SELECT * FROM slugdata WHERE slugname = $1", opp_slug_name)

            opp_slug_level = random.randint(1,10)
            opp_slug_rank = random.randint(1,50)

            opp_attack = opp_slugdata['attack']
            opp_speed = opp_slugdata['speed']
            # endregion
            # region Part 4 : Battle Calculations
            Total_Damage = attack

            opp_slug_damage = opp_slug_attack
            # endregion
            # region Part 5 : Ability Calculations

            # endregion
            # region Part 6 : Damage Calculations [CHECK for Health]
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
