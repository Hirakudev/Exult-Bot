from ._core import CoreDB


class WelcomeDB(CoreDB):
    async def get_config(self, *, guild_id: int):
        async with self.pool.acquire() as conn:
            config = await conn.fetchrow(
                "SELECT * from welcome_config WHERE guild_id=$1", guild_id
            )
            return dict(config)

    async def set_channel(self, *, guild_id: int, channel_id: int = None):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE welcome_config SET channel_id=$1 WHERE guild_id=$2",
                channel_id,
                guild_id,
            )

    async def set_custom_message(self, *, guild_id: int, message: str = None):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE welcome_config SET custom_message=$1 WHERE guild_id=$2",
                message,
                guild_id,
            )
