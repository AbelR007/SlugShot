# Modules
import discord
from discord.ext import commands
from discord.app_commands import AppCommandError
# For Menus
from discord.ext import menus
from discord.ext.menus import button, First, Last
# Other Modules
import os, asyncpg, asyncio
import sys, traceback
from typing import Optional, Literal
# Loading ENV
from dotenv import load_dotenv
load_dotenv()
# =================================================================
# Bot Setup
# Database Connection
async def create_db_pool():
    bot.pg_con = await asyncpg.create_pool(
        database=os.getenv("database_name"),
        user=os.getenv("database_user"),
        password=os.getenv("database_pswd"),
    )

# Custom Prefix
default_prefix = "."
async def custom_prefix(bot, message):
    if message.guild is None:
        return commands.when_mentioned_or(default_prefix)(bot, message)
    else:
        server = int(message.guild.id)
        dbprefix = await bot.pg_con.fetch("SELECT * FROM server WHERE serverid = $1", int(server))
        if not dbprefix:
            await bot.pg_con.execute("INSERT INTO server (serverid, prefix) VALUES ($1, $2)", int(server), default_prefix)
            return commands.when_mentioned_or(default_prefix)(bot, message)
        else:
            current_prefix = str(dbprefix[0]['prefix'])
            return commands.when_mentioned_or(current_prefix)(bot, message)

class SlugShot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix = custom_prefix, 
            intents=discord.Intents.all(),
            status = discord.Status.dnd,
            activity = discord.Activity(
                type=discord.ActivityType.watching, 
                name="you"
            ),
        )
        # self.remove_command("help")
    
    async def setup_hook(self):
        for filename in os.listdir("./super_cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"super_cogs.{filename[:-3]}")
    
    async def on_ready(self):
        print(f"Logged in as {self.user.name}#{self.user.discriminator}")
        await self.setup_hook()
    
bot = SlugShot()
# =================================================================
#region Syncing
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
  ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
#endregion Syncing
#region Slash Error Handler
@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: AppCommandError
):
    await interaction.response.send_message(
        f"An error occurred while processing this command:\n```{error}```",
        ephemeral=True
    )
    # print(f"An error occurred while processing {interaction.command.name}:\n{error}")
    print(f'Ignoring exception in command {interaction.command.name}', file=sys.stderr)
    traceback.print_exception(
        type(error), error, error.__traceback__, file=sys.stderr)
#endregion
# =================================================================
TOKEN = os.getenv('discord_token')

# Main Event Loop
async def main():
    async with bot:
        await create_db_pool()
        await bot.start(TOKEN)
asyncio.run(main())
