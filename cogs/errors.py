import discord
import traceback
import sys
from discord.ext import commands, tasks
from discord.ext.commands.errors import CommandNotFound, MissingPermissions

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def error_embed(self, ctx, content):
        embed = discord.Embed(title="ERROR", description=f"{content}", color=ctx.bot.error)
        embed.set_footer(text="Any doubt? Join the support server")
        return await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        # print(traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr))
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CheckFailure):
            await self.error_embed(ctx, "Permission denied!")
            # embed = discord.Embed(title='😐 Oof. Permission not granted !',
            #                       description=f'Sorry, but you dont have permissions to do that',
            #                       colour=discord.Colour.orange())
            # await ctx.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            await self.error_embed(ctx, "Bot doesn't have the permissions to do the command!")
            # embed = discord.Embed(title='😐 Bot doesn\'t have permissions to do that !',
            #                       description=f'How to rectify it ? Go to Settings > Role > Carbon+ > Kick/Ban Members = True.',
            #                       colour=discord.Colour.orange())
            # await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandOnCooldown):
            await self.error_embed(ctx,"Chill! Command on Cooldown")

        elif isinstance(error, commands.MaxConcurrencyReached):
            await self.error_embed(ctx,"Wait for the completion of the previous command first!")

        elif isinstance(error, commands.BadArgument):
            await self.error_embed(ctx, "Incorrect value entered!")

        elif isinstance(error, commands.MissingRequiredArgument):
            if hasattr(ctx.command, 'on_error'):
                return
            else:
                await self.error_embed(ctx,"Missing Required Arguments. Try again.")
        else:
            user = self.bot.get_user(636181565621141505)
            await user.send("Error occurred!")
            await user.send(
                f"""
                ```
                {error}
                ```
                """
            )
            print("ERROR")
            raise error

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     desc = None
    #     if isinstance(error, commands.CommandNotFound):
    #         pass
    #
    #     elif isinstance(error, commands.CheckFailure):
    #         desc = "Permission Not Granted!"
    #
    #     elif isinstance(error, commands.BotMissingPermissions):
    #         desc = "Bot does not have permission to do that!"
    #
    #     elif isinstance(error, commands.CommandOnCooldown):
    #         desc = "Command on Cooldown! Chill!"
    #
    #     elif isinstance(error, commands.MissingRequiredArgument):
    #         if hasattr(ctx.command,'on_error'):
    #             return
    #         else:
    #             desc = "Missing Required Arguments"
    #
    #     else:
    #         print("ERROR 404\n")
    #         raise error
    #
    #     if desc == None :
    #         return
    #     else:
    #         embed = discord.Embed(
    #             title="Error 404",
    #             description=desc,
    #             color=ctx.bot.error
    #         )
    #         await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Errors(bot))
