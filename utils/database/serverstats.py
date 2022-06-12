from ._core import CoreDB


class ServerStatsDB(CoreDB):
    async def get_config(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                config = await conn.fetchrow(
                    "SELECT * FROM serverstats WHERE guild_id=$1", guild_id
                )
        if not config:
            return config
        return dict(config)

    async def try_config(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                config = await self.get_config(guild_id)
                if not config:
                    config = await self.pool.fetchrow(
                        "INSERT INTO serverstats (guild_id) VALUES ($1) RETURNING *",
                        guild_id,
                    )
        return dict(config)

    async def upload_timezone(
        self, guild_id: int, *, channel_id: int = None, timezone: str = None
    ):
        config = await self.try_config(guild_id)
        if (
            config.get("time_channel") == channel_id
            and config.get("timezone") == timezone
        ):
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                if config.get("time_channel") != channel_id:
                    await conn.execute(
                        "UPDATE serverstats SET time_channel=$1 WHERE guild_id=$2",
                        channel_id,
                        guild_id,
                    )
                if config.get("timezone") != timezone:
                    await conn.execute(
                        "UPDATE serverstats SET timezone=$1 WHERE guild_id=$2",
                        timezone,
                        guild_id,
                    )

    async def upload_milestone(
        self, guild_id: int, *, channel_id: int = None, milestone: str = None
    ):
        config = await self.try_config(guild_id)
        if (
            config.get("milestone_channel") == channel_id
            and config.get("milestone") == milestone
        ):
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                if config.get("milestone_channel") != channel_id:
                    await conn.execute(
                        "UPDATE serverstats SET milestone_channel=$1 WHERE guild_id=$2",
                        channel_id,
                        guild_id,
                    )
                if config.get("milestone") != milestone:
                    await conn.execute(
                        "UPDATE serverstats SET milestone=$1 WHERE guild_id=$2",
                        milestone,
                        guild_id,
                    )

    async def upload_membercount(self, guild_id: int, channel_id: int):
        config = await self.try_config(guild_id)
        if config.get("membercount_channel") == channel_id:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE serverstats SET membercount_channel=$1 WHERE guild_id=$2",
                    channel_id,
                    guild_id,
                )

    async def upload_channels(self, guild_id: int, channel_id: int):
        config = await self.try_config(guild_id)
        if config.get("channels_channel") == channel_id:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE serverstats SET channels_channel=$1 WHERE guild_id=$2",
                    channel_id,
                    guild_id,
                )

    async def upload_statuses(self, guild_id: int, channel_id: int):
        config = await self.try_config(guild_id)
        if config.get("status_channel") == channel_id:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE serverstats SET status_channel=$1 WHERE guild_id=$2",
                    channel_id,
                    guild_id,
                )
