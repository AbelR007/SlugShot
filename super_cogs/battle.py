import discord
from discord.ext import commands
import consts as c
from exts import regions

""" Battle Commands
- /battle
    - /explore
    - /battle bot
"""

class Battle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(
        description = "Understand how SlugShot battle commands work"
    )
    async def battle(self, ctx: commands.Context):
        server = ctx.message.server

        db_server = await self.bot.pg_con.fetchrow("SELECT * FROM server WHERE serverid = $1", server.id)
        prefix = db_server['prefix']

        embed = discord.Embed(
            title = "Battle Commands",
            description = "Battle to improve your slugs and your characters",
            color = c.main
        )
        embed.add_field(
            name = f"{prefix}explore",
            value = "Explore the world to find slugs and items, Battle slugs in the wild with random villagers and npc characters",
            inline = False
        )
        embed.add_field(
            name = f"{prefix}duel @player",
            value = "Challenge another player in a 1v1 slug battle",
            inline = False
        )
        embed.add_field(
            name = f"{prefix}battlebot",
            value = "Battle the Bot for practice to improve strategies and tactics",
            inline = False
        )
        await ctx.send(embed = embed)
    
    @commands.command(
        description = "Explore the caverns beyond the locations",
        aliases = ["x"],
        max_concurrency = commands.MaxConcurrency(1, per = commands.BucketType.user, wait = False)
    )
    async def explore(self, ctx: commands.Context):
        user = ctx.message.author
        user_id = user.id

        #region 1 : Checks if user has STARTed their journey 
        db_profile = await self.profiledb(user_id)
        start = db_profile['start']

        if start == 0:
            start_embed = discord.Embed(
                title = "Retry later",
                description = "You need to start your journey first.\nType `/start` to start your journey",
                color = c.error
            )
            return await ctx.send(embed = start_embed)
        #endregion End of 1

        #region 2 : Gets character specific to the location
        region = db_profile['region']
        location = db_profile['location']
        try:
            opp_chars = regions[region][location]
        except KeyError:
            return await self.error_embed(ctx, "This Cavern is Locked.")
        #endregion End of 2

        # Battle Function
        result = await self.battle(ctx, user_id)
    
    #region Explore Sub Functions
    async def battle(self, ctx: commands.Context, user_id):
        db_profile = await self.profiledb(user_id)

        #region 1 : Gets character details
        char_id = str(db_profile['character'])
        char_type_id = (
            await self.bot.pg_con.fetchrow("SELECT * FROM allchars WHERE charid = $1",char_id)
        )['chartypeid']
        char_name = (
            await self.bot.pg_con.fetchrow("SELECT * FROM chardata WHERE charid = $1",char_id)
        )['charname']
        char_health, char_attack, char_defense, char_speed, char_imgurl = await self.character_data(char_name)
        
        #endregion End of 1
    
    # Battle() SUB Functions
    async def character_data(self, char_name):
        chardb = await self.bot.pg_con.fetchrow("SELECT * FROM chardata WHERE charname = $1", char_name)
        health = int(chardb['health'])
        attack = int(chardb['attack'])
        defense = int(chardb['defense'])
        speed = int(chardb['speed'])
        imgurl = chardb['imgurl']
        return health, attack, defense, speed, imgurl
    #endregion End of Explore Sub Functions



async def setup(bot):
    await bot.add_cog(Battle(bot))
