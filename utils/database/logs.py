import discord

from typing import Union

from ._core import CoreDB


class LogsDB(CoreDB):
    log_types = [
        "guild_logs",
        "join_logs",
        "member_logs",
        "message_logs",
        "moderation_logs",
        "voice_logs",
    ]

    async def new_config(self, guild: Union[discord.Guild, int]):
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO log_config (guild_id) VALUES ($1)", guild_id
                )
        config = await self.get_config(guild_id)

    async def get_config(self, guild: Union[discord.Guild, int]):
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                config = await conn.fetchrow(
                    "SELECT * FROM log_config WHERE guild_id=$1", guild_id
                )
                if config:
                    return dict(config)
        return None

    async def set_log(
        self,
        guild: Union[discord.Guild, int],
        log: str,
        channel: Union[discord.TextChannel, int, None],
    ):
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        channel_id = channel.id if isinstance(channel, discord.TextChannel) else channel
        if log not in self.log_types:
            return False
        config = await self.get_config(guild_id)
        if not config:
            config = await self.new_config(guild_id)
        if config.get(log) == channel_id:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    f"UPDATE log_config SET {log}=$1 WHERE guild_id=$2",
                    channel_id,
                    guild_id,
                )
                return True
