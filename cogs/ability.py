import discord
from discord.ext import commands, tasks

class Ability(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def ability(self, ctx):
        embed = discord.Embed(
            title = "Abilities",
            description = "Every Slug has a unique ability.",
            color = ctx.bot.main
        )
        embed.add_field(
            name = ".ability info <ability name>",
            value = "Shows information regarding the specific ability",
            inline = False
        )
        # embed.add_field(
        #     name = ".ability search"
        # )
        await ctx.send(embed=embed)

    @ability.command()
    async def info(self, ctx, *, name):
        user_id = int(ctx.message.author.id)

        abilitydb = await self.bot.pg_con.fetchrow("SELECT * FROM ability WHERE ability = $1",name)

        if not abilitydb:
            return await ctx.send("No such ability found.")

        embed = discord.Embed(
            color = ctx.bot.main
        )
        embed.set_author(name=f"{name}",icon_url=self.bot.user.avatar_url)
        embed.add_field(name = "Slug", value = abilitydb['slugname'].capitalize())
        embed.add_field(name = "Rarity",value=abilitydb['rarity'])
        embed.add_field(name = "Description",value=abilitydb['desc'],inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Ability(bot))

