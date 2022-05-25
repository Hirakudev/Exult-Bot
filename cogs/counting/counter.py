import discord
from discord.ext import commands

from bot import ExultBot
from utils import *


class Counter(commands.Cog):
    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db = CountingDB(self.bot)

    @commands.Cog.listener(name="on_message")
    async def counting_message(self, msg: discord.Message):
        if any((msg.author.bot, not msg.guild)):
            return
        config = await self.db.get_config(msg.guild)
        if not config:
            return
        channel_id = config.get("channel_id")
        if not channel_id or channel_id != msg.channel.id:
            return

        last_number = config.get("num")
        target = last_number + 1
        last_user = config.get("user_id")
        blacklisted_users = config.get("blacklisted_users")
        blacklisted_roles = config.get("blacklisted_roles")

        if any(r.id in blacklisted_roles for r in msg.author.roles):
            return
        elif msg.author.id in blacklisted_users:
            return

        if msg.content.isdigit():
            if msg.author.id == last_user:
                await msg.add_reaction("❌")
                await self.db.reset_progress(msg.guild.id)
                return "bad"
            if msg.content == str(last_number):
                await msg.add_reaction("❌")
                await self.db.reset_progress(msg.guild.id)
                return "bad"
            if int(msg.content) == target:
                await msg.add_reaction("✅")
                await self.db.add_number(msg.guild.id, msg.author.id)
                return
            await msg.add_reaction("❌")
            await self.db.reset_progress(msg.guild.id)
            return "bad"
        elif any(
            [
                "+" in msg.content,
                "-" in msg.content,
                "*" in msg.content,
                "x" in msg.content,
                "/" in msg.content,
            ]
        ):
            try:
                content = msg.content.replace("x", "*")
                numEntered = eval(content)
            except SyntaxError:
                return
            if msg.author.id == last_user:
                await msg.add_reaction("❌")
                await self.db.reset_progress(msg.guild.id)
                return "bad"
            elif int(numEntered) == last_number:
                await msg.add_reaction("❌")
                await self.db.reset_progress(msg.guild.id)
                return "bad"
            elif numEntered == target:
                await msg.add_reaction("✅")
                await self.db.add_number(msg.guild.id, msg.author.id)
                return
