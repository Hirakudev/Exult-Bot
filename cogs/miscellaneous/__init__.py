import discord

# Discord Imports

from .avatar import Avatar

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Miscellaneous(Avatar):
    """Miscellaneous Cog"""


async def setup(bot: ExultBot):
    await bot.add_cog(Miscellaneous(bot))
