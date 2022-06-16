import discord
from discord import app_commands
from discord.ext import commands

from typing import List

from bot import ExultBot
from .client import LevellingClient
from utils import *


class LevellingCommands(commands.Cog):
    def __init__(self, bot: ExultBot):
        self.bot: ExultBot = bot
        self.client = LevellingClient(bot)
        self.db = self.client.db
        self.cd_mapping = commands.CooldownMapping.from_cooldown(
            1, 60, commands.BucketType.member
        )

    async def get_leaderboard(self, guild_id: int) -> List[dict]:
        users = await self.db.get_users(guild_id)
        if not users:
            return "No users in this server have gained any xp yet!"
        leaderboard = sorted(
            users, key=lambda t: (t.get("level"), t.get("xp")), reverse=True
        )
        return leaderboard

    @commands.Cog.listener(name="on_message")
    async def levelling_on_message(self, message: discord.Message):
        if all((not message.author.bot, message.guild)):
            if message.guild.id == 336642139381301249:  # dpy server
                return
            retry_after = self.cd_mapping.update_rate_limit(message)
            if not retry_after:
                config = await self.db.get_config(message.guild.id)
                if not config:
                    return
                if message.channel.id in config.get("blacklisted_channels"):
                    return
                for role in message.author.roles:
                    if role.id in config.get("blacklisted_roles"):
                        return
                await self.client.add_xp(message.author, message)

    @app_commands.command(
        name="rank", description="View the level of yourself or another member!"
    )
    @app_commands.describe(member="The member who's rank you want to view")
    async def rank_slash(self, itr: discord.Interaction, member: discord.Member = None):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        member = member or itr.user

        user = await self.db.get_user(itr.guild.id, member.id)
        if not user:
            embed = embed_builder(
                title="Oops!",
                description=f"{member.mention} doesn't have any xp! Send a message to start making gains! 💪",
            )
            return await followup.send(embed=embed)

        xp = user.get("xp")
        level = user.get("level")
        required_xp = self.client.formula(level)
        all_users = await self.db.get_users(itr.guild.id)

        profile = [u for u in all_users if u.get("user_id") == member.id]
        rank = all_users.index(profile[0]) + 1

        buffer = await RankCard(bot).make_image(
            member, {"xp": xp, "required_xp": required_xp, "rank": rank, "level": level}
        )
        await followup.send(file=discord.File(fp=buffer, filename="rank.png"))

    @app_commands.command(
        name="leaderboard",
        description="Display all members in the top 10 of the Levelling Leaderboard!",
    )
    async def leaderboard_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        leaderboard = await self.get_leaderboard(itr.guild.id)
        if isinstance(leaderboard, str):
            return await followup.send(leaderboard)
        top_10 = []
        for i in range(0, 10):
            try:
                top_10.append(leaderboard[i])
            except IndexError:
                break

        embed = embed_builder(
            author=[bot.try_asset(itr.guild.icon), f"Top 10 users in {itr.guild.name}"]
        )
        description = ""

        for i, u in enumerate(top_10):
            user = itr.guild.get_member(u.get("user_id"))
            description += f"**{i+1}.** {user}: **Level:** {u.get('level')}\n"
        embed.description = description

        await followup.send(embed=embed)
