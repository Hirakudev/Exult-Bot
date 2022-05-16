import discord
from discord.ext import commands

# Discord Imports

from typing import Generic

# Regular Imports

from bot import ExultBot, EB

# Local Imports


class ExultCog(commands.Cog):
    def __init__(self, bot: ExultBot):
        self.bot: ExultBot = bot


class Interaction(discord.Interaction, Generic[EB]):
    client: EB  # type: ignore


class KnownInteraction(Interaction[EB]):
    guild: discord.Guild  # type: ignore
