from discord import Object
#Discord Imports

from .core import Core
#Cog Imports

from utils import *
#Local Imports

class Moderation(Core):
    """Moderation Cog"""

async def setup(bot: ExultBot):
    await bot.add_cog(Moderation(bot), guilds=[Object(guild) for guild in bot.app_guilds])