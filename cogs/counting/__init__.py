import discord

# Discord Imports

from .config import CountingConfig
from .counter import Counter

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Counting(Counter, CountingConfig):
    """Counting Cog"""


async def setup(bot: ExultBot):
    await bot.add_cog(
        Counting(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds]
    )
