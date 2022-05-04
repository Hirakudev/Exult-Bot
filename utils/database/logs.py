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