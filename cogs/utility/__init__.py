import discord

# Discord Imports

from .emojis import Emojis
from .role import Role
from .customcommands import CustomCommands

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Utility(Emojis, Role, CustomCommands):
    """Utility Cog"""

    db = None
    utils = None


async def setup(bot: ExultBot):
    Utility.db = CustomCommandsDB(bot)
    Utility.utils = CommandUtils(bot)
    await bot.add_cog(Utility(bot))
