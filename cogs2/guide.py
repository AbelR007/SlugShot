import discord
from discord.ext import commands, menus
from discord.ext.menus import button, First, Last

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
        # global dict
        dict = {
            0: {
                "title" : "SlugShot",
                "description" : "New player? `c.start`\nHelp needed? `c.support` ",
                "battle" : "Battle your opponents or against AI opponents",
                "trade" : "Trade your slugs and progress more",
                "explore" : "Go beyond the caverns and explore!",
                "container" : "Keep your precious slugs in containers!",
                "info" : "Know more about the slugs in the game",
            },
            1: {
                "title" : "Battle/Duel",
                "description" : "Battle your opponents or against AI opponents",
                "team": "descsss",
                "profile": "descc",
            },
        }
        no = entries - 1
        title = dict[no]['title']
        desc = dict[no]['description']

        embed = discord.Embed(
            title=title,
            description=desc,
            color=menu.ctx.bot.main
        )
        embed.set_footer(text=f"Page {no} | Requested by {menu.ctx.author}")
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
                value=f"{menu.ctx.bot.tree}{list_values[i]}",
                inline=False
            )
        return embed

class Guide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def guide(self, ctx):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        formatter = MySource(data, per_page=1)
        menu = MyMenuPages(formatter)
        await menu.start(ctx)


def setup(bot):
    bot.add_cog(Guide(bot))