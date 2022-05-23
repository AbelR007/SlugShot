import discord
from discord.ext import commands
import random
import asyncio

"""
STEPs in STARTING your JOURNEY :
1. Get your first slug
2. Get your first blaster & character(will be added later)
3. Basic Duel
4. Finishing Gifts (New random slug)
"""

class Start(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



def setup(bot):
    bot.add_cog(Start(bot))