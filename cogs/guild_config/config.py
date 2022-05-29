import discord
from discord import app_commands

# Discord Imports

# Regular Imports

from bot import ExultBot
from utils import *

# Local Imports


class GuildConfig(ExultCog):

    config = app_commands.Group(
        name="config",
        description="Configure the bot to suit your server's needs!",
        default_permissions=discord.Permissions(manage_guild=True),
    )
