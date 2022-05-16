from ._core import CoreDB


class LevellingDB(CoreDB):
    async def get_user(self, guild_id: int, user_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                user = await conn.fetchrow(
                    "SELECT * FROM levelling_users WHERE guild_id=$1 AND user_id=$2",
                    guild_id,
                    user_id,
                )
                if user:
                    return dict(user)
        return None

    async def new_user(self, guild_id: int, user_id: int, xp: int):
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(
                        "INSERT INTO levelling_users(user_id, guild_id, xp, level) VALUES ($1, $2, $3, $4)",
                        user_id,
                        guild_id,
                        xp,
                        1,
                    )
        except:
            pass
        user = await self.get_user(guild_id=guild_id, user_id=user_id)
        return dict(user)

    async def add_xp(self, guild_id: int, user_id: int, xp: int):
        user = await self.get_user(guild_id=guild_id, user_id=user_id)
        if not user:
            user = await self.new_user(guild_id=guild_id, user_id=user_id, xp=xp)
            return dict(user)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_users SET xp=xp+$1 WHERE user_id=$2 AND guild_id=$3",
                    xp,
                    user_id,
                    guild_id,
                )
        user = await self.get_user(guild_id=guild_id, user_id=user_id)
        return dict(user)

    async def level_up(self, guild_id: int, user_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_users SET level=level+1 WHERE guild_id=$1 AND user_id=$2",
                    guild_id,
                    user_id,
                )
                await conn.execute(
                    "UPDATE levelling_users SET xp=0 WHERE guild_id=$1 AND user_id=$2",
                    guild_id,
                    user_id,
                )
        user = await self.get_user(guild_id=guild_id, user_id=user_id)
        return dict(user)

    async def get_custom_message(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                msg = await conn.fetchval(
                    "SELECT levelup_message FROM levelling_config WHERE guild_id=$1",
                    guild_id,
                )
                return msg

    async def get_custom_channel(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                channel = await conn.fetchval(
                    "SELECT announce_channel FROM levelling_config WHERE guild_id=$1",
                    guild_id,
                )
                return channel

    async def leaderboard(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                leaderboard = await conn.fetch(
                    "SELECT user_id, xp, level FROM levelling_users WHERE guild_id=$1",
                    guild_id,
                )
                leaderboard = [dict(l) for l in leaderboard]
                ldbd = sorted(
                    leaderboard,
                    key=lambda t: (t.get("level"), t.get("xp")),
                    reverse=True,
                )
                return ldbd

    async def set_custom_message(self, guild_id: int, message: str):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_config SET levelup_message=$1 WHERE guild_id=$2",
                    message,
                    guild_id,
                )

    async def set_custom_channel(self, guild_id: int, channel_id):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_config SET announce_channel=$1 WHERE guild_id=$2",
                    channel_id,
                    guild_id,
                )

    async def remove_custom_message(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_config SET levelup_message=$1 WHERE guild_id=$2",
                    None,
                    guild_id,
                )

    async def remove_custom_channel(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_config SET announce_channel=$1 WHERE guild_id=$2",
                    None,
                    guild_id,
                )

    async def get_blacklisted(self, guild_id: int, **kwargs):
        if kwargs.get("get"):
            get = "roles" if kwargs.get("get") == "roles" else "channels"

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                blacklist = await conn.fetchval(
                    f"SELECT blacklisted_{get} FROM levelling_config WHERE guild_id=$1",
                    guild_id,
                )
                if blacklist:
                    return blacklist
        return False

    async def add_blacklisted_channel(self, guild_id: int, channel_id: int):
        blacklisted = await self.get_blacklisted(guild_id=guild_id, get="channels")
        if blacklisted:
            if any(channel_id == channel for channel in blacklisted):
                return False
        if not blacklisted:
            blacklisted = []
        blacklisted.append(channel_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_config SET blacklisted_channels=$1 WHERE guild_id=$2",
                    blacklisted,
                    guild_id,
                )
        return True

    async def add_blacklisted_role(self, guild_id: int, role_id: int):
        blacklisted = await self.get_blacklisted(guild_id=guild_id, get="roles")
        if blacklisted:
            if any(role_id == role for role in blacklisted):
                return False
        if not blacklisted:
            blacklisted = []
        blacklisted.append(role_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_config SET blacklisted_roles=$1 WHERE guild_id=$2",
                    blacklisted,
                    guild_id,
                )
                return True

    async def remove_blacklisted_channel(self, guild_id: int, channel_id: int):
        blacklisted = await self.get_blacklisted(guild_id=guild_id, get="channels")
        if not any(channel_id == channel for channel in blacklisted):
            return False
        blacklisted.remove(channel_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_config SET blacklisted_channels=$1 WHERE guild_id=$2",
                    blacklisted,
                    guild_id,
                )
                return True

    async def remove_blacklisted_role(self, guild_id: int, role_id: int):
        blacklisted = await self.get_blacklisted(guild_id=guild_id, get="roles")
        if not any(role_id == role for role in blacklisted):
            return False
        blacklisted.remove(role_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE levelling_config SET blacklisted_roles=$1 WHERE guild_id=$2",
                    blacklisted,
                    guild_id,
                )
                return True

    async def get_rewards(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                rewards = await conn.fetch(
                    "SELECT level, role FROM levelling_rewards WHERE guild_id=$1",
                    guild_id,
                )
                return dict(rewards)

    async def add_reward(self, guild_id: int, level: int, role_id: int):
        rewards = await self.get_rewards(guild_id=guild_id)
        for key, value in rewards.items():
            if value == role_id:
                return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO levelling_rewards(guild_id, level, role) VALUES ($1, $2, $3)",
                    guild_id,
                    level,
                    role_id,
                )
                return True

    async def remove_reward(self, guild_id: int, level: int, role_id: int):
        rewards = await self.get_rewards(guild_id=guild_id)
        r = []
        for key, value in rewards.items():
            r.append(value)
        if value not in r:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM levelling_rewards WHERE guild_id=$1 AND level=$2 AND role=$3",
                    guild_id,
                    level,
                    role_id,
                )
                return True
