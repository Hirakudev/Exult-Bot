import discord

# Discord Imports

from .eval import Eval
from .sync import Sync

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Admin(Eval, Sync):
    """Admin Cog"""


async def setup(bot: ExultBot):
    await bot.add_cog(
        Admin(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds]
    )
