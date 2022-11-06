import discord
from discord.ext import commands, tasks
from discord.ext.commands.errors import CommandNotFound, MissingPermissions
import consts as c
import traceback, sys
from discord import Interaction
from discord.app_commands import AppCommandError

class Errors(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # bot.tree.on_error = self.on_app_command_error
    
    async def error_embed(self, ctx, no, content):
        embed = discord.Embed(title=f"Error {no}", description=f"{content}",color=c.error)
        embed.set_footer(text="Any doubts? Join the .support server")
        return await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await self.error_embed(ctx, 109,f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                await ctx.send('I could not find that member. Please try again.')

        else:
            await ctx.send(f"{error}")
            print('Ignoring exception in command {}:'.format(
                ctx.command), file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr)
    
    # @commands.Cog.listener()
    # async def on_app_command_error(
    #     self,
    #     interaction: Interaction,
    #     error: AppCommandError
    # ):
    #     print("This error was handled with option 1 from ?tag treeerrorcog")
    #     print(error)
    
    # # @commands.Cog.listener()
    # async def cog_app_command_error(
    #     self,
    #     interaction: Interaction,
    #     error: AppCommandError
    # ):
    #     print("This error was handled with option 2 from ?tag treeerrorcog")
    #     print(error)


async def setup(bot: commands.Bot):
    await bot.add_cog(Errors(bot))
