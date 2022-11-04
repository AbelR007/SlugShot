import random

import discord
from discord.ext import commands
import datetime, time

"""
    ping
    botinfo | about
    invite 
    support
    superping
    # daily
"""

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        description = "Shows the latency of the bot",
        aliases = ['pong']
    )#PING
    async def ping(self, ctx):
        embed = discord.Embed(title = 'Pong !',colour = ctx.bot.success)
        embed.set_footer(text = f'Requested by {ctx.author}')
        embed.add_field(name='Bot Latency :',value=f'{round(self.bot.latency*100)} ms.\nNot Bad !? Not Good !?', inline=False)
        await ctx.send(embed=embed)

    @commands.command(
        description = "Displays information regarding this SlugShot bot",
        aliases = ['botinfo','aboutbot','credits','copyright'],
    )
    async def about(self, ctx):
        embed = discord.Embed(
            title="About SlugShot",
            description="SlugShot is a fan-created Slugterra-series based Discord Game Bot that provides entertainment to Slugterra fans and everyone in general. Catch, Trade, and Duel Slugs in an ever-updating Bot.",
            colour=ctx.bot.main
        )
        embed.add_field(name="Total Servers :", value=f"{len(self.bot.guilds)}",inline=True)
        embed.add_field(name="Total Users :", value=f"{len(self.bot.users)}",inline=True)
        embed.add_field(name="Owner :", value=f"<@636181565621141505>",inline=True)
        embed.add_field(
            name="Affiliation/Policy :",
            value=f"*SlugShot Bot is NOT affiliated with Slugterra, ESI, or WildBrain.*\nSlugShot is a Fan-created Discord Bot based on the Slugterra shows.",
            inline=False,
        )
        embed.add_field(
            name="Media From :",
            value = f"Media files as in the character skins/ slug images are from Fandom Wikipedia",
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(
        description = "Provides the invite link for the SlugShot Bot",
        aliases=['invitebot','botlink'],
    )
    async def invite(self, ctx):
        embed = discord.Embed(
            title="Invite Slugshot",
            description=f"[As Administrator](https://discord.com/api/oauth2/authorize?client_id=744238855724466238&permissions=8&scope=bot)\n[With Basic Bot Permissions](https://discord.com/api/oauth2/authorize?client_id=744238855724466238&permissions=1256479652928&scope=bot)", colour=ctx.bot.main)
        await ctx.send(embed=embed)

    @commands.command(
        description = "Provides link to the SlugShot Support Server",
        aliases = ['supp']
    )
    async def support(self, ctx):
        embed = discord.Embed(
            title = "Support Needed?",
            description= "Join the [Official SlugShot Support Server](https://discord.io/slugshot)\nOR need to suggest anything? use `.support`",
            color = ctx.bot.main
        )
        await ctx.send(embed=embed)

    @commands.command(
        description = "Provides an accurate ping to the Bot",
        hidden=True,
    )
    async def superping(self, ctx):
        start = time.perf_counter()
        message = await ctx.send("Ping...")
        end = time.perf_counter()
        duration = (end - start) * 1000
        await message.edit(content='Pong! {:.2f}ms'.format(duration))

    # @commands.command()
    # @commands.cooldown(1, 86400, commands.BucketType.user)
    # async def daily(self, ctx):
    #     member_id = int(ctx.message.author.id)
    #     daily_coins = random.randint(60, 120)
    #
    #     user = await self.bot.pg_con.fetch("SELECT * FROM profile WHERE userid = $1", int(member_id))
    #     cur_coins = user[0]['gold']
    #     now = cur_coins + daily_coins
    #     tada = '\U0001f389'
    #     emoji = ctx.bot.gold
    #
    #     await self.bot.pg_con.execute("UPDATE profile SET gold = $1 WHERE userid = $2", now, member_id)
    #     embed = discord.Embed(
    #         title=f'Congrats {ctx.message.author.name} {tada}',
    #         description=f'You got {daily_coins} {emoji} as your DAILY Reward. Be Sure to collect them everyday.',
    #         colour=ctx.bot.success,
    #         timestamp=ctx.message.created_at
    #     )
    #     await ctx.send(embed=embed)
    #
    # @daily.error
    # async def daily_command_error(self, ctx, error):
    #     if isinstance(error, commands.CommandOnCooldown):
    #         embed = discord.Embed(title='😅 Daily Command on Cooldown for 1 day !',
    #                               description=f'You have already claimed your Daily ammount...\nTime to claim is not yet here !',
    #                               colour=discord.Colour.orange())
    #         embed.set_footer(text='Play with other commands available...')
    #         await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
