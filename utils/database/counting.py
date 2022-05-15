from typing import Union

from ._core import CoreDB


class CountingDB(CoreDB):
    async def get_config(self, *, guild_id: int):
        async with self.pool.acquire() as conn:
            config = await conn.fetchrow(
                "SELECT * FROM counting_config WHERE guild_id=$1", guild_id
            )
            if config:
                return config
        return None

    async def set_config(self, *, guild_id: int, channel_id: int = None):
        async with self.pool.acquire() as conn:
            config = await self.get_config(guild_id=guild_id)
            if not config:
                await conn.execute(
                    "INSERT INTO counting_config (guild_id, channel_id, num, user_id) VALUES ($1, $2, $3, $3)",
                    guild_id,
                    channel_id,
                    0,
                )
                return
            await conn.execute(
                "UPDATE counting_config SET channel_id=$1 WHERE guild_id=$2",
                channel_id,
                guild_id,
            )
            await conn.execute(
                "UPDATE counting_config SET num=$1 WHERE guild_id=$2", 0, guild_id
            )
            await conn.execute(
                "UPDATE counting_config SET user_id=$1 WHERE guild_id=$2", 0, guild_id
            )

    async def remove_config(self, *, guild_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM counting_config WHERE guild_id=$1", guild_id
            )

    async def reset_progress(self, *, guild_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE counting_config SET num=$1 WHERE guild_id=$2", 0, guild_id
            )
            await conn.execute(
                "UPDATE counting_config SET user_id=$1 WHERE guild_id=$2", 0, guild_id
            )

    async def add_num(self, *, guild_id: int, user_id: int):
        config = await self.get_config(guild_id=guild_id)
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE counting_config SET num=$1 WHERE guild_id=$2",
                config["num"] + 1,
                guild_id,
            )
            await conn.execute(
                "UPDATE counting_config SET user_id=$1 WHERE guild_id=$2",
                user_id,
                guild_id,
            )

    async def set_channel(self, *, guild_id: int, channel: Union[int, None]):
        config = await self.get_config(guild_id=guild_id)
        if config:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "UPDATE counting_config SET channel_id=$1 WHERE guild_id=$2",
                    channel,
                    guild_id,
                )
            return True
        await self.set_config(guild_id=guild_id, channel_id=channel)

    async def add_blacklisted_role(self, *, guild_id: int, role_id: int):
        config = await self.get_config(guild_id=guild_id)
        if any(role_id == role for role in config["blacklisted_roles"]):
            return False
        config["blacklisted_roles"].append(role_id)
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE counting_config SET blacklisted_roles=$1 WHERE guild_id=$2",
                config["blacklisted_roles"],
                guild_id,
            )
        return True

    async def add_blacklisted_user(self, *, guild_id: int, user_id: int):
        config = await self.get_config(guild_id=guild_id)
        if any(user_id == user for user in config["blacklisted_users"]):
            return False
        config["blacklisted_users"].append(user_id)
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE counting_config SET blacklisted_users=$1 WHERE guild_id=$2",
                config["blacklisted_users"],
                guild_id,
            )
        return True

    async def remove_blacklisted_role(self, *, guild_id: int, role_id: int):
        config = await self.get_config(guild_id=guild_id)
        if not any(role_id == role for role in config["blacklisted_roles"]):
            return False
        config["blacklisted_roles"].remove(role_id)
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE counting_config SET blacklisted_roles=$1 WHERE guild_id=$2",
                config["blacklisted_roles"],
                guild_id,
            )
        return True

    async def remove_blacklisted_user(self, *, guild_id: int, user_id: int):
        config = await self.get_config(guild_id=guild_id)
        if not any(user_id == user for user in config["blacklisted_users"]):
            return False
        config["blacklisted_users"].remove(user_id)
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE counting_config SET blacklisted_users=$1 WHERE guild_id=$2",
                config["blacklisted_users"],
                guild_id,
            )
        return True

    async def get_blacklisted(self, *, guild_id: int, **kwargs):
        if kwargs.get("get"):
            get = "users" if kwargs.get("get") == "users" else "roles"

        async with self.pool.acquire() as conn:
            blacklist = await conn.fetchval(
                f"SELECT blacklisted_{get} FROM counting_config WHERE guild_id=$1",
                guild_id,
            )
        if len(blacklist):
            return blacklist
        return False
