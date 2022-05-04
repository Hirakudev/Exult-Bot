import discord
#Discord Imports

from .avatar import Avatar
from .role import Role
from .userinfo import UserInfo
#Cog Imports

from bot import ExultBot
from utils import *
#Local Imports


class Miscellaneous(Avatar, Role, UserInfo):
    """ Miscellaneous Cog """

async def setup(bot: ExultBot):
    await bot.add_cog(Miscellaneous(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds])