import discord

# Discord Imports

from .customcommands import CustomCommands
from .emojis import Emojis
from .role import Role

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Utility(CustomCommands, Emojis, Role):
    """Utility Cog"""


async def setup(bot: ExultBot):
    await bot.add_cog(
        Utility(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds]
    )
