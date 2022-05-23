import discord
from discord.ext import commands


class Server_Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        description="Settings regarding prefix changes",
        aliases=['setprefix']
    )
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, prefix: str = '.'):
        embed = discord.Embed(
            title='Processing...',
            color = ctx.bot.main
        )
        bin = await ctx.send(embed=embed)
        server = int(ctx.message.guild.id)
        default_prefix = '.'
        dbserver = await self.bot.pg_con.fetch("SELECT * FROM server WHERE serverid = $1", server)
        if not dbserver:
            await self.bot.pg_con.execute("INSERT INTO server (serverid, prefix) VALUES ($1, $2)", server,
                                          default_prefix)
        dbserver = await self.bot.pg_con.fetch("SELECT * FROM server WHERE serverid = $1", server)

        await self.bot.pg_con.execute("UPDATE server SET prefix = $1 WHERE serverid = $2", prefix, server)
        embed2 = discord.Embed(title="Done! Prefix Changed",
                               description=f"This server's prefix has been changed to `{prefix}`", colour=ctx.bot.main)
        await bin.edit(embed=embed2)

    @commands.command(
        description="Settings for the Server",
        aliases = ['server setup','setup server','server','ss']
    )
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        channel = ctx.message.channel
        channelid = int(ctx.message.channel.id)
        server = int(ctx.message.guild.id)
        default_prefix = '.'
        dbserver_check = await self.bot.pg_con.fetch("SELECT * FROM server WHERE serverid = $1", server)
        if not dbserver_check:
            await self.bot.pg_con.execute("INSERT INTO server (serverid, prefix) VALUES ($1, $2)", server,
                                          default_prefix)
        dbserver = await self.bot.pg_con.fetch("SELECT * FROM server WHERE serverid = $1", server)
        prefix = dbserver[0]['prefix']

        channel1 = dbserver[0]['channel1']
        channel2 = dbserver[0]['channel2']
        channel3 = dbserver[0]['channel3']
        channel4 = dbserver[0]['channel4']
        channel5 = dbserver[0]['channel5']
        channel6 = dbserver[0]['channel6']

        embed = discord.Embed(
            title='Server Setup',
            description= f"Prefix : `{prefix}`",
            colour=ctx.bot.main
        )
        embed.add_field(
            name="What do you want to do ?",
            value='''
            1️⃣ Add Bot Channel
            2️⃣ Remove Bot Channel
            3️⃣ View Settings
            '''
        )
        embed.set_footer(text='Use reactions')
        timeout_embed = discord.Embed(
            title='Time\'s Up !', description="No changes to your server settings.", colour=ctx.bot.main)

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        await msg.add_reaction("3️⃣")

        def check(reaction, user):
            return user == ctx.message.author and (
                        str(reaction.emoji) == '1️⃣' or str(reaction.emoji) == '2️⃣' or str(reaction.emoji) == '3️⃣')

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            await msg.edit(embed=timeout_embed)
        else:
            if str(reaction.emoji) == '1\N{variation selector-16}\N{combining enclosing keycap}':
                await msg.edit(embed=None, content="Processing...")
                if channelid == (channel1 or channel2 or channel3 or channel4 or channel5 or channel6):
                    await msg.edit(embed=None, content=f"This Channel <#{channelid}> already is a SlugShot channel.")
                else:
                    if channel1 == None:
                        await self.bot.pg_con.execute("UPDATE server SET channel1 = $1 WHERE serverid = $2", channelid,
                                                      server)
                        embed2 = discord.Embed(
                            title="Added Channel", description=f"<#{channelid}> Channel Added.", colour=ctx.bot.main)
                        await msg.edit(embed=embed2, content=None)
                    elif channel2 == None:
                        await self.bot.pg_con.execute("UPDATE server SET channel2 = $1 WHERE serverid = $2", channelid,
                                                      server)
                        embed2 = discord.Embed(
                            title="Added Channel", description=f"<#{channelid}> Channel Added.", colour=ctx.bot.main)
                        await msg.edit(embed=embed2, content=None)
                    elif channel3 == None:
                        await self.bot.pg_con.execute("UPDATE server SET channel3 = $1 WHERE serverid = $2", channelid,
                                                      server)
                        embed2 = discord.Embed(
                            title="Added Channel", description=f"<#{channelid}> Channel Added.", colour=ctx.bot.main)
                        await msg.edit(embed=embed2, content=None)
                    elif channel4 == None:
                        await self.bot.pg_con.execute("UPDATE server SET channel4 = $1 WHERE serverid = $2", channelid,
                                                      server)
                        embed2 = discord.Embed(
                            title="Added Channel", description=f"<#{channelid}> Channel Added.", colour=ctx.bot.main)
                        await msg.edit(embed=embed2, content=None)
                    elif channel5 == None:
                        await self.bot.pg_con.execute("UPDATE server SET channel5 = $1 WHERE serverid = $2", channelid,
                                                      server)
                        embed2 = discord.Embed(
                            title="Added Channel", description=f"<#{channelid}> Channel Added.", colour=ctx.bot.main)
                        await msg.edit(embed=embed2, content=None)
                    elif channel6 == None:
                        await self.bot.pg_con.execute("UPDATE server SET channel6 = $1 WHERE serverid = $2", channelid,
                                                      server)
                        embed2 = discord.Embed(
                            title="Added Channel", description=f"<#{channelid}> Channel Added.", colour=ctx.bot.main)
                        await msg.edit(embed=embed2, content=None)
                    else:
                        await msg.edit(embed=None,
                                       content="6 Channel Slots are filled in. Remove a channel to add a new one")

            elif str(reaction.emoji) == "2\N{variation selector-16}\N{combining enclosing keycap}":
                embed3 = discord.Embed(
                    title="Remove Channel", description="Send the channel here :", colour=ctx.bot.main)
                await msg.edit(embed=None, content="Processing...")
                if channelid == (channel1 or channel2 or channel3 or channel4 or channel5 or channel6):
                    if channel1 == channelid:
                        await self.bot.pg_con.execute("UPDATE server SET channel1 = $1 WHERE serverid = $2", None,
                                                      server)
                        embed2 = discord.Embed(
                            title="Removed Channel", description=f"<#{channelid}> Channel removed from Channel 1 slot",
                            colour=ctx.bot.main)
                        await msg.edit(embed=embed2, content=None)
                    elif channel2 == channelid:
                        await self.bot.pg_con.execute("UPDATE server SET channel2 = $1 WHERE serverid = $2", None,
                                                      server)
                        embed2 = discord.Embed(
                            title="Removed Channel", description=f"<#{channelid}> Channel removed from Channel 2 slot",
                            colour=ctx.bot.main)
                        await msg.edit(embed=embed2, content=None)
                    elif channel3 == channelid:
                        await self.bot.pg_con.execute("UPDATE server SET channel3 = $1 WHERE serverid = $2", None,
                                                      server)
                        embed2 = discord.Embed(
                            title="Removed Channel", description=f"<#{channelid}> Channel removed from Channel 3 slot",
                            colour=ctx.bot.main)
                        await msg.edit(embed=embed2, content=None)
                    elif channel4 == channelid:
                        await self.bot.pg_con.execute("UPDATE server SET channel4 = $1 WHERE serverid = $2", None,
                                                      server)
                        embed2 = discord.Embed(
                            title="Removed Channel", description=f"<#{channelid}> Channel removed from Channel 4 slot",
                            colour=ctx.bot.main)
                        await msg.edit(embed=embed2, content=None)
                    elif channel5 == channelid:
                        await self.bot.pg_con.execute("UPDATE server SET channel5 = $1 WHERE serverid = $2", None,
                                                      server)
                        embed2 = discord.Embed(
                            title="Removed Channel", description=f"<#{channelid}> Channel removed from Channel 5 slot",
                            colour=ctx.bot.main)
                        await msg.edit(embed=embed2, content=None)
                    elif channel6 == channelid:
                        await self.bot.pg_con.execute("UPDATE server SET channel6 = $1 WHERE serverid = $2", None,
                                                      server)
                        embed2 = discord.Embed(
                            title="Removed Channel", description=f"<#{channelid}> Channel removed from Channel 6 slot",
                            colour=ctx.bot.main)
                        await msg.edit(embed=embed2, content=None)
                    else:
                        await msg.edit(embed=None, content="6 Channel slots are EMPTY. Add a new channel to remove one")

                else:
                    await msg.edit(embed=None,
                                   content=f"This Channel <#{channelid}> already is NOT a SlugShot channel. Add it!")

            elif str(reaction.emoji) == "3\N{variation selector-16}\N{combining enclosing keycap}":
                embed4 = discord.Embed(
                    title="View Settings", description="Check which channels does SlugShot has access to :",
                    colour=ctx.bot.main)
                chanl1 = self.bot.get_channel(channel1)
                chanl2 = self.bot.get_channel(channel2)
                chanl3 = self.bot.get_channel(channel3)
                chanl4 = self.bot.get_channel(channel4)
                chanl5 = self.bot.get_channel(channel5)
                chanl6 = self.bot.get_channel(channel6)
                embed4.add_field(name="Channel 1", value=chanl1)
                embed4.add_field(name="Channel 2", value=chanl2)
                embed4.add_field(name="Channel 3", value=chanl3)
                embed4.add_field(name="Channel 4", value=chanl4)
                embed4.add_field(name="Channel 5", value=chanl5)
                embed4.add_field(name="Channel 6", value=chanl6)
                await msg.edit(embed=embed4)

            else:
                await msg.edit(embed=embed)
                await channel.send("It worked.")


def setup(bot):
    bot.add_cog(Server_Settings(bot))
