import discord
from discord.ext import commands
import random


class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # async def battle_function(self, ctx):

    # async def choice_embed(self, ctx, char_name, slug_name):

    async def result_embed(self, ctx, char_name, opp_name, first_slug_name, first_slug_attack, sec_slug_name,
                           sec_slug_attack):
        result_embed = discord.Embed(
            description=f"""
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
            title=f"{char_name} lost. {opp_name} won!",
            color=ctx.bot.main
        )
        final_embed.set_author(name=f"{char_name} VS {opp_name}")
        await ctx.send(embed=final_embed)

    @commands.command(
        description="Battle against your opponents",
        aliases=['duel']
    )
    async def battle(self, ctx, opp: discord.Member = None):
        user_id = int(ctx.message.author.id)
        user_name = str(ctx.message.author.name)

        if opp is None:
            error_embed = discord.Embed(
                title="Error",
                description="Please tag someone for a battle,\nor checkout `c.battlebot` or `c.career` or `c.explore`",
                color=ctx.bot.invis
            )
            return await ctx.send(embed=error_embed)

        opp_id = int(opp.id)
        opp_name = str(opp.name)

    async def battle_function(self, char_name, opp_name):
        await ctx.send("WIP")

    async def slug_emoji(self, slug_id):
        allslugsdb = await self.bot.pg_con.fetch("SELECT * FROM allslugs WHERE slugid = $1", slug_id)
        slugemoji = \
        (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", allslugsdb[0]['slugname']))[0][
            'slugemoji']
        return slugemoji

    @commands.command(
        description="Battle against Bots and AI",
        aliases=['botbattle', 'battleai', 'bb']
    )
    async def battlebot(self, ctx):
        user_id = int(ctx.message.author.id)
        user_name = str(ctx.message.author.name)

        # region Profile Database
        profiledb = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        if not profiledb:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold, crystal, gem) VALUES ($1, $2, $3, $4)",
                                          user_id, 0, 0, 0)
        profiledb = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", user_id)
        cgold = int(profiledb[0]['gold'])
        gold_prize = random.randint(20, 60)
        gold = cgold + gold_prize
        # endregion

        # region User's Character Details through Database
        char_name = str(profiledb[0]['character'])
        # await self.battle_function(self, char_name, opp_name)
        chardb = await self.bot.pg_con.fetch("SELECT * FROM chardata WHERE charname = $1", char_name)
        char_health = int(chardb[0]['health'])
        char_attack = int(chardb[0]['attack'])
        char_imgurl = chardb[0]['imgurl']
        # endregion

        # region Slugs IDs and Emojis using that (for battle embed)
        slug1_id = profiledb[0]['team1']
        slugemoji1 = await self.slug_emoji(slug1_id)
        slug2_id = profiledb[0]['team2']
        slugemoji2 = await self.slug_emoji(slug2_id)
        slug3_id = profiledb[0]['team3']
        slugemoji3 = await self.slug_emoji(slug3_id)
        slug4_id = profiledb[0]['team4']
        slugemoji4 = await self.slug_emoji(slug4_id)
        # endregion

        # region Opponent's Characters [Stats - Health, Attack, Defense]
        oppchars = ['Kord Zane', 'Trixie', 'Pronto']
        opp_name = opp_char_name = random.choice(oppchars)
        oppchardb = await self.bot.pg_con.fetch("SELECT * FROM chardata WHERE charname = $1", opp_name)
        opp_health = opp_char_health = int(oppchardb[0]['health'])
        opp_attack = opp_char_attack = int(oppchardb[0]['attack'])
        opp_defense = opp_char_defense = int(oppchardb[0]['defense'])
        opp_imgurl = oppchardb[0]['imgurl']
        # endregion

        # region Opponent's Slugs Name and Emojis
        opp_slug1 = oppchardb[0]['slug1']
        opp_slug1_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug1))[0]['slugemoji']
        opp_slug2 = oppchardb[0]['slug2']
        opp_slug2_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug2))[0]['slugemoji']
        opp_slug3 = oppchardb[0]['slug3']
        opp_slug3_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug3))[0]['slugemoji']
        opp_slug4 = oppchardb[0]['slug4']
        opp_slug4_emoji = (await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug4))[0]['slugemoji']
        # endregion

        while True:
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
            # todo : to create an auto-editing embed that edits after every battle action

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
            # it returns slug name and slug total attack

            # region Returns the Slug Attack, IV, EV, Speed & Level
            allslugsdb = await self.bot.pg_con.fetch("SELECT * FROM allslugs WHERE slugid = $1", slug_id)
            slug_name = allslugsdb[0]['slugname']
            slug_level = allslugsdb[0]['level']
            slug_ivattack = allslugsdb[0]['iv_attack']
            slug_evattack = allslugsdb[0]['ev_attack']
            slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", slug_name)
            slug_attack = slugdatadb[0]['attack']
            slug_speed = slugdatadb[0]['speed']
            # endregion

            # region Opponent's Choice of Slug [Since bot, its random]
            opp_slug_name = random.choice([opp_slug1, opp_slug2, opp_slug3, opp_slug4])
            opp_slugdatadb = await self.bot.pg_con.fetch("SELECT * FROM slugdata WHERE slugname = $1", opp_slug_name)
            opp_slug_level = random.randint(1, 10)
            opp_slug_attack = opp_slugdatadb[0]['attack']
            opp_slug_speed = opp_slugdatadb[0]['speed']
            # endregion

            # region BATTLE Calculations
            slug_base_attack = int((2 * slug_attack + slug_ivattack + (0.25 * slug_evattack)) * (1 / 2))
            slug_total_attack = int(slug_base_attack + (slug_base_attack * slug_level * 0.01) + slug_level * 1.5)
            slug_damage = int(slug_total_attack + (slug_total_attack / 2 * (char_attack / opp_defense) * 0.09))
            # print(slug_base_attack, slug_total_attack, slug_damage)

            opp_slug_damage = opp_slug_attack
            # endregion

            # print(char_health, opp_health, char_health<=0, opp_health<=0)

            if opp_slug_speed > slug_speed:
                char_health = char_health - opp_slug_damage
                opp_health = opp_health - slug_damage
                if char_health <= 0:
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
                    return
                elif opp_health <= 0:
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
                    return await ctx.send(embed=final_embed)
                else:
                    result_embed = discord.Embed(
                        description=f"""
                            **{opp_name} used {opp_slug_name}**!                         
                            {opp_slug_name.capitalize()} dealt {opp_slug_attack} damage
                            **{char_name} used {slug_name}**!
                            {slug_name.capitalize()} dealt {slug_damage} damage
                        """,
                        color=ctx.bot.main
                    )
                    result_embed.set_author(name=f"{char_name} vs {opp_name}")
                    await ctx.send(embed=result_embed)

            elif slug_speed > opp_slug_speed:
                opp_health -= slug_damage
                char_health = char_health - opp_slug_damage
                if opp_health <= 0:
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
                    return await ctx.send(embed=final_embed)
                elif char_health <= 0:
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
                    return
                else:
                    result_embed = discord.Embed(
                        description=f"""
                            **{char_name} used {slug_name}**!
                            {slug_name.capitalize()} dealt {slug_damage} damage
                            **{opp_name} used {opp_slug_name}**!                         
                            {opp_slug_name.capitalize()} dealt {opp_slug_attack} damage
                        """,
                        color=ctx.bot.main
                    )
                    result_embed.set_author(name=f"{char_name} vs {opp_name}")
                    await ctx.send(embed=result_embed)
            else:  # when slug_speed == opp_slug_speed
                opp_health = opp_health - slug_damage
                char_health = char_health - opp_slug_damage
                if opp_health <= 0:
                    final_embed = discord.Embed(
                        description=
                        f"""
                        **{char_name} used {slug_name}**!
                        {opp_name} lost the rest of its health!

                        {char_name} won the battle! You won!
                        You recieved {gold_prize}{ctx.bot.coins} coins!
                        
                        Good Game!
                        """,
                        color=ctx.bot.main
                    )
                    final_embed.set_author(name=f"Battle Results", url=f"{char_imgurl}")
                    await self.bot.pg_con.execute("UPDATE profile SET gold = $1 WHERE userid = $2", gold, user_id)
                    await ctx.send(embed=final_embed)
                    return
                elif char_health <= 0:
                    final_embed = discord.Embed(
                        description=f"""
                            ****{opp_name} used {opp_slug_name}**!
                            {char_name} lost the rest of its health!

                            {opp_name} won the battle! You lost!
                            Good Game!
                        """,
                        color=ctx.bot.main
                    )
                    final_embed.set_author(name=f"Battle Results", url=f"{opp_imgurl}")
                    await ctx.send(embed=final_embed)
                    return
                else:
                    # Battle results after calculations
                    result_embed = discord.Embed(
                        description=f"""
                            **{char_name} used {slug_name}**!
                            {slug_name.capitalize()} dealt {slug_damage} damage
                            **{opp_name} used {opp_slug_name}**!                         
                            {opp_slug_name.capitalize()} dealt {opp_slug_attack} damage
                        """,
                        color=ctx.bot.main
                    )
                    result_embed.set_author(name=f"{char_name} vs {opp_name}")
                    await ctx.send(embed=result_embed)
        # END of BATTLE


def setup(bot):
    bot.add_cog(Battle(bot))
