import discord
from discord.ext import commands
# Slash Commands
from discord import Interaction, app_commands
# Constants
import consts as c

""" Pod Commands
- /pod view
- /pod info
- /pod buy
"""
def new_pod_position(pos):
    if pos is None:
        return None
    elif pos == '':
        return None
    else:
        npos = pos.split('-')
        return npos[-1]

class PodCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    group = app_commands.Group(name="pod",description="...")

    async def profiledb(self, user_id):
        author = await self.bot.pg_con.fetchrow("SELECT * FROM profile WHERE userid = $1", user_id)
        if not author:
            await self.bot.pg_con.execute("INSERT INTO profile(userid, gold, crystal, gem) VALUES ($1, $2, $3, $4)",
                                          user_id, 0, 0, 0)
        author = await self.bot.pg_con.fetchrow("SELECT * FROM profile WHERE userid = $1", user_id)
        return author

    async def sl(self, coln, posn, authorid):

        author = await self.profiledb(authorid)

        position = str(coln) + "-" + str(posn)
        
        db_allslugs = await self.bot.pg_con.fetchrow(
            "SELECT * FROM allslugs WHERE pod_position = $1 and pod_no = $2 and userid = $3",
            posn, coln, authorid
        )
        if not db_allslugs:
            return "<:blank2:714849946574258188>" # "\u2800\u2800"
        
        db_allslugs = await self.bot.pg_con.fetchrow(
            "SELECT * FROM allslugs WHERE pod_position = $1 and pod_no = $2 and userid = $3",
            posn, coln, authorid
        )
        slugname = db_allslugs['slugname']

        db_slugdata = await self.bot.pg_con.fetchrow("SELECT * FROM slugdata WHERE slugname = $1", slugname)
        slugemoji = db_slugdata['slugemoji']
        
        return slugemoji
    
    @group.command(
        description = "Displays slugs in the pod"
    )
    @app_commands.rename(
        no = "number"
    )
    @app_commands.describe(
        no = "Type the pod number to view"
    )
    async def view(self, interaction: Interaction, no: int = 1, user: discord.Member = None):
        if not user:
            user = interaction.user
        
        user_id = user.id
        db_profile = await self.profiledb(user_id)
        pods = db_profile['pods']
        if no > pods:
            no_embed = discord.Embed(
                title = "Nah!",
                description = "You haven't unlocked that many pods yet!\nYour current pod count is **{}**".format(pods),
                color = c.error
            )
            no_embed.set_footer(text = "You can unlock more pods by /pod buy")
            return await interaction.response.send_message(embed = no_embed)

        n = no
        a = user_id
        embed = discord.Embed(
            title = f"Pod {no}",
            description = f"""
            <:blank2:714849946574258188>|\U0001f1e6|\U0001f1e7|\U0001f1e8|\U0001f1e9|\U0001f1ea
            1️⃣ {await self.sl(n, 'a1', a)} {await self.sl(n, 'b1', a)} {await self.sl(n, 'c1', a)} {await self.sl(n, 'd1', a)} {await self.sl(n, 'e1', a)}
            2️⃣ {await self.sl(n, 'a2', a)} {await self.sl(n, 'b2', a)} {await self.sl(n, 'c2', a)} {await self.sl(n, 'd2', a)} {await self.sl(n, 'e2', a)}
            3️⃣ {await self.sl(n, 'a3', a)} {await self.sl(n, 'b3', a)} {await self.sl(n, 'c3', a)} {await self.sl(n, 'd3', a)} {await self.sl(n, 'e3', a)}
            4️⃣ {await self.sl(n, 'a4', a)} {await self.sl(n, 'b4', a)} {await self.sl(n, 'c4', a)} {await self.sl(n, 'd4', a)} {await self.sl(n, 'e4', a)}
            5️⃣ {await self.sl(n, 'a5', a)} {await self.sl(n, 'b5', a)} {await self.sl(n, 'c5', a)} {await self.sl(n, 'd5', a)} {await self.sl(n, 'e5', a)}
            """,
            color = c.main
        )
        await interaction.response.send_message(embed = embed)
    
    @group.command(
        description = "Shows slug information in the pod"
    )
    async def info(self, interaction: Interaction, no: int):
        
        await interaction.response.send_message("This")
    
    @group.command(
        description = "Buy's you a new pod to store slugs in"
    )
    async def buy(self, interaction: Interaction):
        user = interaction.user
        db_profile = await self.profiledb(user.id)
        pods = db_profile['pods']
        if (pods+1) > 20:
            embed = discord.Embed(
                title = "Nah!",
                description = "You've reached the maximum pod limit of **20**",
                color = c.error
            )
            return await interaction.response.send_message(embed = embed)
        
        cost = 1000 * (pods+1)
        if db_profile['gold'] < cost:
            embed = discord.Embed(
                title = "Nah!",
                description = "You don't have enough gold to buy this pod!\nYou need **{}**{} gold".format(cost, c.gold),
                color = c.error
            )
            return await interaction.response.send_message(embed = embed)
        
        await self.bot.pg_con.execute(
            "UPDATE profile SET gold = $1, pods = $2 WHERE userid = $3", 
            db_profile['gold'] - cost, pods+1, user.id
        )

        embed = discord.Embed(
            title = "Bought!",
            description = f"You bought a new pod!\nPod No. {pods+1}\nCost: {cost}{c.gold}\n\nYou can view your pod by `/pod view`",
            color = c.success
        )
        await interaction.response.send_message(embed = embed)
    
    # @group.command()
    # async def reformat(self, interaction: Interaction):

    #     db_allslugs = await self.bot.pg_con.fetch(
    #         "SELECT * FROM allslugs"
    #     )
    #     allslugs = len(db_allslugs)
    #     for i in range(allslugs):
    #         pod_position = db_allslugs[i]['pod_position']
    #         if pod_position == 'None':
    #             slugid = db_allslugs[i]['slugid']
    #             await self.bot.pg_con.execute(
    #                 "UPDATE allslugs SET pod_position = $1 WHERE slugid = $2",
    #                 None, slugid
    #             )
    #     await interaction.response.send_message("Done")

async def setup(bot: commands.Bot):
    await bot.add_cog(PodCog(bot))
