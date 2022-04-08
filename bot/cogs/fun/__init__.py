from discord import Object
#Discord Imports

from utils import *
#Local Imports


class Fun():
    """ Fun Cog """

async def setup(bot: ExultBot):
    await bot.add_cog(Fun(bot), guilds=[Object(guild) for guild in bot.app_guilds])