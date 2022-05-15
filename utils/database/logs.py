from ._core import CoreDB

# Local Imports


class LogsDB(CoreDB):
    async def get_moderation_logs(self, guild_id):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                log = await conn.fetchval(
                    "SELECT moderation_logs FROM log_config WHERE guild_id=$1", guild_id
                )
                if log:
                    return log
        return None

    async def get_config(self, *, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                config = await conn.fetchrow(
                    "SELECT * FROM log_config WHERE guild_id=$1", guild_id
                )
                if config:
                    return dict(config)
        return None

    async def set_log(self, *, guild_id: int, log: str, channel_id):
        config = await self.get_config(guild_id=guild_id)
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
