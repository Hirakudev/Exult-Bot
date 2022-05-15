import discord
from discord.ext import commands

from bot import ExultBot
from utils import *


class Counter(commands.Cog):
    @commands.Cog.listener(name="on_message")
    async def counting_message(self, msg: discord.Message):
        if any((msg.author.bot, not msg.guild)):
            return
        config = await CountingDB(self.bot).get_config(guild_id=msg.guild.id)
        if not config["channel_id"] or config["channel_id"] != msg.channel.id:
            return

        last_number = config["num"]
        target = last_number + 1
        last_user = config["user_id"]
        blacklisted_users = config["blacklisted_users"]
        blacklisted_roles = config["blacklisted_roles"]

        if any(r.id in blacklisted_roles for r in msg.author.roles):
            return
        elif msg.author.id in blacklisted_users:
            return

        if msg.content.isdigit():
            if msg.author.id == last_user:
                await msg.add_reaction("❌")
                await CountingDB(self.bot).reset_progress(guild_id=msg.guild.id)
                return "bad"
            if msg.content == str(last_number):
                await msg.add_reaction("❌")
                await CountingDB(self.bot).reset_progress(guild_id=msg.guild.id)
                return "bad"
            if int(msg.content) == target:
                await msg.add_reaction("✅")
                await CountingDB(self.bot).add_num(
                    guild_id=msg.guild.id, user_id=msg.author.id
                )
                return
            await msg.add_reaction("❌")
            await CountingDB(self.bot).reset_progress(guild_id=msg.guild.id)
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
                await CountingDB(self.bot).reset_progress(guild_id=msg.guild.id)
                return "bad"
            elif int(numEntered) == last_number:
                await msg.add_reaction("❌")
                await CountingDB(self.bot).reset_progress(guild_id=msg.guild.id)
                return "bad"
            elif numEntered == target:
                await msg.add_reaction("✅")
                await CountingDB(self.bot).add_num(
                    guild_id=msg.guild.id, user_id=msg.author.id
                )
                return
