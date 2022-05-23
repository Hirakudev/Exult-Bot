import discord

# Discord Imports

import os

# Regular Imports

from .config import CurrencyConfig
from .currencycommands import CurrencyCommands
from .handler import CurrencyHandler

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Currency(CurrencyCommands, CurrencyHandler, CurrencyConfig):
    """Currency Cog"""


async def setup(bot: ExultBot):
    await bot.add_cog(
        Currency(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds]
    )
