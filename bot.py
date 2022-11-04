# Discord Modules
import discord
from discord.ext import commands
# for menus
from discord.ext import menus
from discord.ext.menus import button, First, Last
# Other Modules
import os
import asyncpg
import asyncio
# Loading Dot envs
from dotenv import load_dotenv
load_dotenv()
# =================================================================
# Database Connection


async def create_db_pool():  # Connecting with Database
    bot.pg_con = await asyncpg.create_pool(
        database=os.getenv('database_name'),
        user=os.getenv('database_user'),
        password=os.getenv('database_pswd'),
    )
# =================================================================
# Prefix
default_prefix = "."


async def custom_prefix(bot, message):  # Custom Prefix
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
# =================================================================
# Bot cursor
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
class SlugShotBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=custom_prefix,
            intents=intents,
            status=discord.Status.dnd
        )

    async def setup_hook(self):
        for filename in os.listdir("./super_cogs"):
            if filename == "consts.py":
                continue
            if filename.endswith(".py"):
                await self.load_extension(f"super_cogs.{filename[:-3]}")

    async def on_ready(self):
        print(f"Logged in as {self.user.name}#{self.user.discriminator}")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you"))
        await self.setup_hook()

bot = SlugShotBot()
# bot.remove_command('help')
# =================================================================
# Colour Schemes
bot.main = discord.Colour.from_rgb(255, 133, 51)
bot.success = discord.Colour.green()
bot.green = discord.Colour.green()
# discord.Color.from_rgb(48,49,54)  # discord.Colour.orange()
bot.error = discord.Colour.red()
bot.invis = discord.Color.from_rgb(48, 49, 54)  # "0x2F3136"
# Default Emojis
bot.coins = bot.gold = "<:gold:975692828116148265>"  # "\U0001fa99"
bot.crystal = "<:crystal:975692828430725120>"
bot.gem = "<:gems:975692827910610984>"

bot.arrow = '<a:arrow:853303138799190046>'
bot.slugshot = '<:SlugShot:853303301637144596>'
bot.mark = '<:questionmark:853303949540327425>'
bot.branch = '<:tree:974961679148417045>'
bot.question_mark = "<:question_mark:976450883049111582>"
# Color schemes for Embeds
bot.cfire = discord.Colour.from_rgb(255, 102, 51)
bot.cwater = discord.Colour.from_rgb(0, 128, 255)
bot.cice = discord.Colour.from_rgb(0, 255, 255)
bot.cenergy = discord.Colour.from_rgb(121, 255, 77)
bot.celectric = discord.Colour.from_rgb(255, 204, 0)
bot.cpsychic = discord.Colour.from_rgb(255, 102, 204)
bot.cmetal = discord.Colour.from_rgb(194, 214, 214)
bot.cearth = discord.Colour.from_rgb(179, 0, 0)
bot.cplant = discord.Colour.from_rgb(119, 255, 51)
bot.cair = discord.Colour.from_rgb(204, 204, 255)
bot.ctoxic = discord.Colour.from_rgb(198, 83, 198)
bot.cdark = discord.Colour.from_rgb(102, 0, 51)
# Emojis for Types
bot.fire = '<:Fire:846347965283041321>'
bot.water = "<:Water2:846955422224351232>"
bot.ice = '<:Ice2:846952072784248842>'
bot.energy = '<:Energy:846363402552344606>'
bot.electric = '<:Electric:846365499905277954>'
bot.psychic = '<:Psychic:846451290137821194>'
bot.earth = '<:Earth:847110422807969802>'
bot.metal = '<:Metal:847035330057338921>'
bot.plant = '<:Plant3:846957323876302858>'
bot.air = '<:Air3:847116616344928286>'
bot.toxic = '<:Toxic:847112905573138473>'
bot.dark = '<:Dark:846401070027636766>'
# Emojis for Rarities

bot.common = '<:Common:846998735833530380>'
bot.uncommon = '<:Uncommon:846998735710978089>'
bot.rare = '<:Rare:846998733777272833>'
bot.super_rare = '<:SuperRare:846998732880740412>'
bot.mythical = '<:Mythical:846998734591361064>'
bot.legendary = '<:Legendary:846998735049195550>'

# region Help Commands
# ===============================================================================
# class MyHelp(commands.MinimalHelpCommand):
#     def get_command_signature(self, command):
#         return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

#     # colour_id =
#     async def send_bot_help(self, mapping):
#         if self.context.author.id != 636181565621141505:
#             return await self.get_destination().send("Use `.menu` command to get a list of helpful commands")
#         embed = discord.Embed(
#             title="SlugShot", description="Use the .menu for a better understanding", colour=bot.main)
#         for cog, commands in mapping.items():
#             filtered = await self.filter_commands(commands, sort=True)
#             command_signatures = [
#                 self.get_command_signature(c) for c in commands
#             ]
#             # print(command_signatures)
#             if command_signatures:
#                 cog_name = getattr(cog, "qualified_name", "No Category")
#                 if cog_name == "No Category":
#                     continue
#                 embed.add_field(name=cog_name,
#                                 value="{}".format(str(command_signatures).strip(
#                                     '[]').replace('\'', '`').replace(',', ' ')),
#                                 inline=False)
#                 # print(command_signatures)

#         channel = self.get_destination()
#         embed.set_footer(text="< > Required  |  [ ] Optional ")
#         await channel.send(embed=embed)
#         dmembed = discord.Embed(
#             title="Welcome to SlugShot Arena!",
#             color=bot.main
#         )
#         dmembed.add_field(
#             name="i) Easy to use",
#             value="Simple, yet unique! That's how we designed SlugShot!",
#             inline=False
#         )
#         dmembed.add_field(
#             name="ii) Level up by Chatting or Battling",
#             value="Slugs gain experience from duels and Characters gain experience from chatting",
#             inline=False
#         )
#         dmembed.add_field(
#             name="iii) Explore",
#             value="Explore unknown locations and catch new slugs and improve your arsenal!",
#             inline=False
#         )
#         dmembed.add_field(
#             name="iv) New Slugs",
#             value="Slugs are everything in SlugShot. That's why, we are constantly trying to add new features for complexity, yet simple for battles.",
#             inline=False
#         )
#         dmembed.add_field(
#             name="v) Constantly updating",
#             value="Unlike other bots, SlugShot is constantly updating with new slugs, new locations and new features",
#             inline=False
#         )
#         dmembed.add_field(
#             name="Join the Official SlugShot Server :  https://discord.gg/YjaAw44fj5",
#             value="We are one active interactive community! If you are in need of help or support, this is the one place you need to be!",
#             inline=False
#         )
#         dmembed.set_author(
#             name="SlugShot", icon_url=self.context.bot.user.avatar_url)
#         dmembed.set_footer(text="By AbelR#4070 | SlugShot Developer")
#         await self.context.author.send(embed=dmembed)

#     async def send_command_help(self, command):
#         embed = discord.Embed(
#             title=self.get_command_signature(command), color=bot.main)
#         # if command.description is None:
#         #     command.description = 'None'
#         # embed.add_field(name="Description :", value=command.description)
#         desc = command.description
#         if desc:
#             embed.add_field(name="Description :",
#                             value=f"{desc}", inline=False)
#         alias = command.aliases
#         if alias:
#             embed.add_field(
#                 name="Aliases :", value=", ".join(alias), inline=False)

#         channel = self.get_destination()
#         embed.set_footer(text="< > Required  |  [ ] Optional ")
#         await channel.send(embed=embed)

#     async def on_help_command_error(self, ctx, error):
#         if isinstance(error, commands.BadArgument):
#             embed = discord.Embed(title="Error", description=str(error))
#             await ctx.send(embed=embed)
#         else:
#             raise error


# =================================================================
dict = {
    0: {
        "title": "SlugShot",
        "description": "New player? `.start`\nHelp needed? `.support` ",

        "battle": "Battle your opponents or against AI opponents",
        "explore": "Go beyond the caverns and explore!",
        "profile": "Check out your profile, team, and arsenal",
        "slugs": "Manage your arsenal and upgrade it to its max!",
        "info": "Know about Slugs & Characters available in SlugShot",
        "settings": "Settings for the Server",
        "other": "Other numerous bot commands for the SlugShot bot",
    },
    1: {
        "title": "Battle/Duel",
        "description": "Battle your opponents or against AI opponents",
        "battlebot": "Battle against the Bot [Random Characters]",
        "duel @user": "Duel against a friend/rival",
    },
    2: {
        "title": "Explore",
        "description": "To catch new slugs, explore unknown caverns, and be a slugshot master!",

        "explore": "Explore the caverns beyond the locations",
        "goto <location>": "To go to a specific location",
        "location": "Displays your current location and region",
        "slugloc":"Shows all slugs available in all locations",

        "career": "...",
    },
    3: {
        "title": "Profile",
        "description": "Shows your and profile data",
        "profile [user]": "Shows your profile data",
        "team [user]": "Shows your battling team",
        "wallet [user]": "Displays your gold & crystals",
        "bag": "...",
    },
    4: {
        "title": "Slugs",
        "description": "Manage your arsenal and upgrade it to its max!",
        "info <slug name>": "Shows the info about the slugs [Base Stats]",
        "sluginfo <position>": "Shows the info about your slugs",
        "arsenal [box number]": "Displays all your slugs in your arsenal",

        "boxswap <position 1> <position 2>": "Swap slugs inside your arsenal(box) itself",
        "swap <team position> <box position>": "Swaps your slug in your team and your arsenal",
        "release <box position>": "Releases a slug present in your arsenal"
    },

    5: {
        "title": "Server Settings",
        "description": "Displays settings for the server [Only admins can change settings]",

        "prefix <new prefix>": "Changes server prefix [By default it is `.`]",
        "settings": "Shows settings for the server",
    },

    6: {
        "title": "Other Commands",
        "description": "General commands for the SlugShot bot",

        "support": "Shows the link to the Official SlugShot Support Server",
        "invite": "Displays the invite link for the bot",
        "about": "Displays information about the bot",
        "ping": "Shows the bot's ping",
    }
}


class MyMenuPages(menus.MenuPages, inherit_buttons=False):
    @button('\U000023ea', position=First(0))
    async def go_to_first_page(self, payload):
        await self.show_page(0)

    @button('\U000025c0', position=First(1))
    async def go_to_previous_page(self, payload):
        await self.show_checked_page(self.current_page - 1)

    @button('\U000025b6', position=Last(1))
    async def go_to_next_page(self, payload):
        await self.show_checked_page(self.current_page + 1)

    @button('\U000023e9', position=Last(2))
    async def go_to_last_page(self, payload):
        max_pages = self._source.get_max_pages()
        last_page = max(max_pages - 1, 0)
        await self.show_page(last_page)

    @button('\U000023f9', position=Last(0))
    async def stop_pages(self, payload):
        self.stop()


class MySource(menus.ListPageSource):
    # def __init__(self, bot):
    #     self.bot = bot
    async def format_page(self, menu, entries):

        no = int(entries) - 1
        title = dict[no]['title']
        desc = dict[no]['description']

        embed = discord.Embed(
            title=title,
            description=desc,
            color=menu.ctx.bot.main
        )
        if no == 0:
            embed.set_footer(
                text=f"Page {no} | Requested by {menu.ctx.author}")
        else:
            embed.set_footer(
                text=f"Page {no} | Use .help command to know more about the command")
        # embed.set_author(name="SlugShot",icon_url= menu.bot.avatar_url)

        list_keys = list(dict[no].keys())
        list_values = list(dict[no].values())
        length = len(list_keys)

        for i in range(2, length):
            if no == 0:
                prefix = ""
            else:
                prefix = "."
            embed.add_field(
                name=f"{prefix}{list_keys[i]} ",
                value=f"{menu.ctx.bot.branch}{list_values[i]}",
                inline=False
            )
        return embed
# class MyHelp(commands.MinimalHelpCommand):
#     async def send_pages(self):
#         data = [1,2,3,4,5]
#         menulist = MySource(data, per_page=1)
#         menu = MyMenuPages(menulist, delete_message_after=True)
#         await menu.start(self.context)


@bot.command(aliases=['menu'])
async def guide(ctx):
    data = [1, 2, 3, 4, 5, 6, 7]
    menulist = MySource(data, per_page=1)
    menu = MyMenuPages(menulist, delete_message_after=True)
    await menu.start(ctx)

# endregion# =================================================================
# =================================================================
# Running Database
TOKEN = os.getenv('discord_token')


async def main():
    async with bot:
        # await bot.loop.run_until_complete(create_db_pool())
        await create_db_pool()
        await bot.start(TOKEN)
asyncio.run(main())
# =================================================================
# Discord Token Env
# bot.run(os.getenv('discord_token'))
