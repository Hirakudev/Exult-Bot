import discord
from discord.ext import commands

from utils import *


class GuildJoin(ExultCog):
    @commands.Cog.listener(name="on_guild_join")
    async def add_guild(self, guild: discord.Guild):
        await GuildsDB(self.bot).add_guild(guild.id)

        async for log in guild.audit_logs(
            limit=1, action=discord.AuditLogAction.bot_add
        ):
            added_by = log.user
        users = len([user for user in guild.members if not user.bot])
        bots = len([user for user in guild.members if user.bot])
        total = len(guild.members)
        risk = True if bots > users or bots > 25 else False

        guilds = len(self.bot.guilds)
        _users = len(self.bot.users)

        embed = embed_builder(
            title=f"New guild joined",
            description=f"""
                         **Name:** {guild.name}
                         **Owner:** {guild.owner} | `{guild.owner.id}`
                         **Added by:** {added_by} | `{added_by.id}`
                         **Total Users:**
                         👨 {users} | 🤖 {bots} | 💫 {total}
                         **Bot Farm Risk:** `{'No' if not risk else 'Yes'}`""",
            author=[
                self.bot.try_asset(self.bot.user.avatar),
                f"Guilds: {guilds} | Users: {_users}",
            ],
            colour=self.bot.green,
            thumbnail=self.bot.try_asset(guild.icon),
            footer=f"ID: {guild.id}",
        )
        await self.bot.bot_logs.send(
            content="" if not risk else self.bot.dev_role.mention, embed=embed
        )
