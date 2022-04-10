from discord import Object
#Discord Imports

#Cog Imports

from utils import *
#Local Imports

class Config():
    """ Config Cog """

async def setup(bot: ExultBot):
    await bot.add_cog(Config(bot), guilds=[Object(guild) for guild in bot.app_guilds])
