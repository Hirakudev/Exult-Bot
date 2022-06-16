import discord

# Discord Imports

from .emojis import Emojis
from .role import Role

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Utility(Emojis, Role):
    """Utility Cog"""


async def setup(bot: ExultBot):
    await bot.add_cog(Utility(bot))
