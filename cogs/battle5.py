import discord
from discord.ext import commands
import random


class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def error_embed(self, ctx, content):
        embed = discord.Embed(title="ERROR",description=f"{content}",color=ctx.bot.error)
        return await ctx.send(embed=embed)

    async def slug_emoji(self, slug_id):
        allslugsdb = await self.bot.pg_con.fetch("SELECT * FROM allslugs WHERE slugid = $1", slug_id)
        slugemoji = \
            (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", allslugsdb[0]['slugname']))[0][
                'slugemoji']
        return slugemoji

    async def profiledb(self, user_id):
        profiledb = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        if not profiledb:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold, crystal, gem) VALUES ($1, $2, $3, $4)",
                                          user_id, 0, 0, 0)
        profiledb = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        return profiledb

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

    async def you_won_embed(self, ctx, user_id, char_name, opp_name, slug_name, char_imgurl, gold_prize, gold):
        final_embed = discord.Embed(
            description=
            f"""
                    **{char_name} used {slug_name.capitalize()}**!
                    {opp_name} lost the rest of its health!

                    {char_name} won the battle! You won!
                    You recieved {gold_prize}{ctx.bot.coins} coins.

                    Good Game!
                    """,
            color=ctx.bot.main
        )
        final_embed.set_author(name=f"Battle Results", url=f"{char_imgurl}")
        await self.bot.pg_con.execute("UPDATE profile SET gold = $1 WHERE userid = $2", gold, user_id)

    async def action_embed(self, ctx, first_name, first_slug_name, first_slug_damage, second_name, second_slug_name, second_slug_damage):
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

    @commands.command(
        description="Battle against Bots and AI",
        aliases=['botbattle', 'battleai', 'bb']
    )
    async def battlebot(self, ctx):
        user_id = int(ctx.message.author.id)
        # user = ctx.message.author
        user_name = str(ctx.message.author.name)

        # region Profile Database
        profiledb = await self.profiledb(user_id)
        start = profiledb[0]['start']
        if start == 0:
            start_embed = discord.Embed(title = "Retry later",description="Please start your journey first using `.start`\nAny doubts? Ask at SlugShot support server",color=ctx.bot.invis)
            return await ctx.send(embed=start_embed)

        # Gold rewarded after match [Randomised]
        cgold = int(profiledb[0]['gold'])
        gold_prize = random.randint(20, 60)
        gold = cgold + gold_prize
        # endregion

        # region User's Character Details
        char_name = str(profiledb[0]['character'])
        chardb = await self.bot.pg_con.fetch("SELECT * FROM chardata WHERE charname = $1", char_name)
        char_health = int(chardb[0]['health'])
        char_attack = int(chardb[0]['attack'])
        char_defense = int(chardb[0]['defense'])
        char_speed = int(chardb[0]['speed'])
        char_imgurl = chardb[0]['imgurl']
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
        opp_characters = ['Kord Zane', 'Trixie', 'Pronto']
        opp_name = random.choice(opp_characters)
        oppchardb = await self.bot.pg_con.fetch("SELECT * FROM chardata WHERE charname = $1", opp_name)
        opp_health = int(oppchardb[0]['health'])
        opp_attack = int(oppchardb[0]['attack'])
        opp_defense = int(oppchardb[0]['defense'])
        opp_imgurl = oppchardb[0]['imgurl']
        # endregion

        # region Opponent's Slug Names and Emojis
        opp_slug1 = oppchardb[0]['slug1']
        opp_slug1_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug1))[0][
            'slugemoji']
        opp_slug2 = oppchardb[0]['slug2']
        opp_slug2_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug2))[0][
            'slugemoji']
        opp_slug3 = oppchardb[0]['slug3']
        opp_slug3_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug3))[0][
            'slugemoji']
        opp_slug4 = oppchardb[0]['slug4']
        opp_slug4_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug4))[0][
            'slugemoji']
        # endregion

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
            await ctx.send(embed=battle_embed)
            # endregion

            # region Input for Action [Slug Choice]
            def check(a):
                return a.author == ctx.message.author and (
                        (a.content == "1") or (a.content == "2") or (a.content == "3") or (a.content == "4") or (
                        a.content == "ff"))

            # Waiting for User's Command
            msg = await self.bot.wait_for('message', check=check)
            choice = msg.content

            if choice == "1":
                slug_id = slug1_id
            elif choice == "2":
                slug_id = slug2_id
            elif choice == "3":
                slug_id = slug3_id
            elif choice == "4":
                slug_id = slug4_id
            elif choice == "ff":
                return await ctx.send("You forfeit!")
            else:
                return await ctx.send("Enter a valid option | Retry later")
            # endregion

            # region User's Slug Details
            allslugsdb = await self.bot.pg_con.fetch("SELECT * FROM allslugs WHERE slugid = $1", slug_id)
            slug_name = allslugsdb[0]['slugname']
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
            opp_slug_level = random.randint(1, 10)
            opp_slug_attack = opp_slugdatadb[0]['attack']
            opp_slug_speed = opp_slugdatadb[0]['speed']
            # endregion

            # region BATTLE Calculations for USER & OPPONENT
            # user
            slug_base_attack = int((2 * slug_attack + slug_ivattack + (0.25 * slug_evattack)) * (1 / 2))
            slug_total_attack = int(slug_base_attack + (slug_base_attack * slug_level * 0.01) + slug_level * 1.5)
            slug_damage = int(slug_total_attack + (slug_total_attack / 2 * (char_attack / opp_defense) * 0.09))

            # opponent
            opp_slug_damage = opp_slug_attack
            # endregion

            # print(char_health, opp_health, char_health<=0, opp_health<=0)
            #region Damage Details [CHECK for Health]
            if opp_slug_speed > slug_speed:
                char_health = char_health - opp_slug_damage
                opp_health = opp_health - slug_damage
                if char_health <= 0:
                    return await self.you_lost_embed(ctx, char_name, opp_name, opp_imgurl, opp_slug_name)
                elif opp_health <= 0:
                    return await self.you_won_embed(ctx, user_id, char_name, opp_name, slug_name, char_imgurl, gold_prize, gold)
                else:
                    await self.action_embed(ctx, opp_name, opp_slug_name, opp_slug_damage, char_name, slug_name, slug_damage)

            elif slug_speed > opp_slug_speed:
                opp_health -= slug_damage
                char_health = char_health - opp_slug_damage
                if opp_health <= 0:
                    return await self.you_won_embed(ctx, user_id, char_name, opp_name, slug_name, char_imgurl, gold_prize, gold)
                elif char_health <= 0:
                    return await self.you_lost_embed(ctx, char_name, opp_name, opp_imgurl, opp_slug_name)
                else:
                    await self.action_embed(ctx, char_name, slug_name, slug_damage, opp_name, opp_slug_name, opp_slug_damage)

            else:  # when slug_speed == opp_slug_speed
                opp_health = opp_health - slug_damage
                char_health = char_health - opp_slug_damage
                if opp_health <= 0:
                    return await self.you_won_embed(ctx, user_id, char_name, opp_name, slug_name, char_imgurl, gold_prize, gold)
                elif char_health <= 0:
                    return await self.you_lost_embed(ctx, char_name, opp_name, opp_imgurl, opp_slug_name)
                else:
                    await self.action_embed(ctx, char_name, slug_name, slug_damage, opp_name, opp_slug_name, opp_slug_damage)
            #endregion
        # END of BATTLE BoT

    @commands.command(
        description = "Duel with your allies or your rivals!",
        aliases = ['battle']
    )
    async def duel(self, ctx, opp : discord.Member):
        return await ctx.send("Work in Progress!")
        user_id = int(ctx.message.author.id)
        user = ctx.message.author
        user_name = ctx.message.author.name
        opp_id = opp.id
        opp_name = opp.name

        if opp.id == user_id:
            # error_embed = discord.Embed(title="ERROR",description="You can't challenge yourself!",color=ctx.bot.error)
            # return await ctx.send(embed=error_embed)
            return await self.error_embed(ctx, "You can't challenge yourself!")
        if opp.bot is True:
            return await self.error_embed(ctx, "You can't challenge a bot")

        profiledb = await self.profiledb(user_id)
        start = profiledb[0]['start']
        if start == 0:
            start_embed = discord.Embed(title = "Retry later",description="Please start your journey first using `.start`\nAny doubts? Ask at SlugShot support server",color=ctx.bot.invis)
            return await ctx.send(embed=start_embed)

        # Gold rewarded after match [Randomised]
        cgold = int(profiledb[0]['gold'])
        gold_prize = random.randint(20, 60)
        # endregion

        # region User's Character Details
        char_name = str(profiledb[0]['character'])
        chardb = await self.bot.pg_con.fetch("SELECT * FROM chardata WHERE charname = $1", char_name)
        char_health = int(chardb[0]['health'])
        char_attack = int(chardb[0]['attack'])
        char_defense = int(chardb[0]['defense'])
        char_speed = int(chardb[0]['speed'])
        char_imgurl = chardb[0]['imgurl']
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

        opp_profiledb = await self.profiledb(opp_id)
        opp_start = opp_profiledb[0]['start']
        if opp_start == 0:
            start_embed = discord.Embed(title="Retry later",
                                        description="Please start your journey first using `.start`\nAny doubts? Ask at SlugShot support server",
                                        color=ctx.bot.invis)
            return await ctx.send(embed=start_embed)

        # Gold rewarded after match [Randomised]
        opp_cgold = int(opp_profiledb[0]['gold'])
        # endregion

        # region Opponent's Character Details
        opp_char_name = str(opp_profiledb[0]['character'])
        opp_chardb = await self.bot.pg_con.fetch("SELECT * FROM chardata WHERE charname = $1", opp_char_name)
        opp_char_health = opp_health = int(opp_chardb[0]['health'])
        opp_char_attack = opp_attack = int(opp_chardb[0]['attack'])
        opp_char_defense = opp_defense = int(opp_chardb[0]['defense'])
        opp_char_speed = opp_speed = int(opp_chardb[0]['speed'])
        opp_char_imgurl = opp_imgurl = opp_chardb[0]['imgurl']
        # endregion

        # region Opponent's Slugs IDs and Emojis
        opp_slug1_id = opp_profiledb[0]['team1']
        opp_slug1_emoji = await self.slug_emoji(opp_slug1_id)
        opp_slug2_id = opp_profiledb[0]['team2']
        opp_slug2_emoji = await self.slug_emoji(opp_slug2_id)
        opp_slug3_id = opp_profiledb[0]['team3']
        opp_slug3_emoji = await self.slug_emoji(opp_slug3_id)
        opp_slug4_id = opp_profiledb[0]['team4']
        opp_slug4_emoji = await self.slug_emoji(opp_slug4_id)
        # endregion

        #region Duel Request
        ask_embed = discord.Embed(
            title="Duel Challenge",
            description=f"**{user_name} has challenged you to a duel.**\nDo you accept or not?",
            color = ctx.bot.main
        )
        ask_embed.set_footer(text="Reply 'accept' or 'decline'")
        start_embed = await ctx.send(opp.mention, embed = ask_embed)
        def ask_check(a):
            return a.author == opp and (a.content == "accept" or a.content == "decline")
        ask = await self.bot.wait_for('message',check=ask_check)
        if ask.content == "accept":
            ask_embed2 = discord.Embed(title="Duel Started",description="The Duel has been started in your DMs.",color=ctx.bot.main)
            await start_embed.edit(embed=ask_embed2)
        if ask.content == "decline":
            ask_embed2 = discord.Embed(title="Duel Request Declined",description=f"{opp.mention} has declined your duel request!",color=ctx.bot.main)
            return await start_embed.edit(embed = ask_embed2)
        #endregion

        while True:
            # region Battle Embed
            battle_embed = discord.Embed(
                title=f"{user_name} VS {opp_name}",
                color=ctx.bot.main
            )
            battle_embed.add_field(
                name=f"{char_name}",
                value=f"Health : {char_health}\nSlugs : {slugemoji1}{slugemoji2}{slugemoji3}{slugemoji4}",
                inline=False
            )
            battle_embed.add_field(
                name=f"{opp_char_name}",
                value=f"Health : {opp_health}\nSlugs : {opp_slug1_emoji}{opp_slug2_emoji}{opp_slug3_emoji}{opp_slug4_emoji}",
                inline=False
            )
            battle_embed.set_footer(text="Choose your option : 1, 2, 3, 4 or 'ff'")
            await user.send(embed=battle_embed)
            await opp.send(embed=battle_embed)
            # endregion

            # region Input for Action [Slug Choice]
            def check(a):
                return a.author == ctx.message.author and (
                        (a.content == "1") or (a.content == "2") or (a.content == "3") or (a.content == "4") or (
                        a.content == "ff"))

            # Waiting for User's Command
            msg = await self.bot.wait_for('message', check=check)
            choice = msg.content

            if choice == "1":
                slug_id = slug1_id
            elif choice == "2":
                slug_id = slug2_id
            elif choice == "3":
                slug_id = slug3_id
            elif choice == "4":
                slug_id = slug4_id
            elif choice == "ff":
                return await ctx.send("You forfeit!")
            else:
                return await ctx.send("Enter a valid option | Retry later")
            # endregion

    @duel.error
    async def duel_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title = "ERROR",
                description = """
                    You can't duel alone! You have to mention someone.
                    For eg,
                    .duel <@636181565621141505>
                             
                    If you have to practice alone, battle a bot using `.battlebot`
                    or you can explore the caverns using `.explore`
                """,
                color= ctx.bot.error
            )
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Battle(bot))
