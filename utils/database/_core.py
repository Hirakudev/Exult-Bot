import discord

# Discord Imports

from typing import TYPE_CHECKING

# Regular Imports
if TYPE_CHECKING:
    from bot import ExultBot
    import asyncpg

# Local Imports


class CoreDB:
    def __init__(self, bot: "ExultBot" = None):
        self.bot: "ExultBot" = bot
        self.pool: "asyncpg.Pool" = bot.pool
