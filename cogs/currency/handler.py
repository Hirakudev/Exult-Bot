import discord
from discord import app_commands
from discord.ext import commands

import random

from bot import ExultBot
from utils import *


class CurrencyHandler(commands.Cog):
    """Currency Event Handler"""

    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db = CurrencyDB(bot)

    cd_mapping = commands.CooldownMapping.from_cooldown(
        1, 30, commands.BucketType.member
    )
    give_on_message = True

    @commands.Cog.listener("on_message")
    async def currency_message(self, message: discord.Message):
        if self.give_on_message:
            if any(
                (
                    message.author.bot,
                    not message.guild,
                )
            ):
                return
            if message.guild.id != self.bot._guild:
                return
            retry_after = self.cd_mapping.update_rate_limit(message)
            if not retry_after:
                num = random.randint(1, 5)
                await self.db.update_wallet(message.guild.id, message.author.id, num)
