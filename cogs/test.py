import discord
from discord.ext import commands
from PIL import Image, ImageFont, ImageDraw

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def photo(self, ctx):
        abc = await ctx.send("Processing.....")
        pro = ctx.message.author.avatar_url
        helvetica = ImageFont.truetype(r"D:\Projects\SlugShot\fonts\bebas_neue.ttf", size=40)
        d = ImageDraw.Draw(pro)
        name = ctx.message.author.name

        location = (100, 100)
        text_color = (100, 100, 200)
        d.text(location, f"{name}", font=helvetica, fill=text_color)
        await ctx.send(file= discord.File(pro))
        await ctx.send("Done")

async def setup(bot):
    await bot.add_cog(Test(bot))