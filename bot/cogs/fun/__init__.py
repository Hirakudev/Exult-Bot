from discord import Object
#Discord Imports

from .wtp import WTP
from .basic import Basic
from .weather import Weather
#Cog Imports

from utils import *
#Local Imports


class Fun(WTP, Basic, Weather):
    """ Fun Cog """

async def setup(bot: ExultBot):
    await bot.add_cog(Fun(bot), guilds=[Object(guild) for guild in bot.app_guilds])