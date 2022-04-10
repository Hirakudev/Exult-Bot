from discord import Object
#Discord Imports


#Cog Imports

from utils import *
#Local Imports


class Miscellaneous():
    """ Miscellaneous Cog """

async def setup(bot: ExultBot):
    await bot.add_cog(Miscellaneous(bot), guilds=[Object(guild) for guild in bot.app_guilds])