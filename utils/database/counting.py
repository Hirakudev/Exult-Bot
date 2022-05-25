import discord

from typing import Union, List

from ._core import CoreDB


class CountingDB(CoreDB):
    async def new_config(
        self, guild: Union[discord.Guild, int], channel: Union[discord.TextChannel, int]
    ) -> None:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        channel_id = channel.id if isinstance(channel, discord.TextChannel) else channel
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO counting_config (guild_id, channel_id) VALUES ($1, $2)",
                    guild_id,
                    channel_id,
                )

    async def get_config(self, guild: Union[discord.Guild, int]) -> Union[dict, None]:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                config = await conn.fetchrow(
                    "SELECT * FROM counting_config WHERE guild_id=$1", guild_id
                )
            if config:
                return dict(config)
        return None

    async def delete_config(self, guild: Union[discord.Guild, int]) -> bool:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        config = await self.get_config(guild_id)
        if not config:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM counting_config WHERE guild_id=$1", guild_id
                )
                return True

    async def reset_progress(self, guild: Union[discord.Guild, int]) -> bool:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        config = await self.get_config(guild_id)
        if not config:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE counting_config SET num=$1, user_id=$1 WHERE guild_id=$2",
                    0,
                    guild_id,
                )
                return True

    async def set_channel(
        self,
        guild: Union[discord.Guild, int],
        channel: Union[discord.TextChannel, int, None],
    ) -> bool:
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        channel_id = channel.id if isinstance(channel, discord.TextChannel) else channel
        config = await self.get_config(guild_id)
        if not config:
            return False
        if config.get("channel_id") == channel_id:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE counting_config SET channel_id=$1 WHERE guild_id=$2",
                    channel_id,
                    guild_id,
                )
                return True

    async def blacklist_add(
        self,
        guild: Union[discord.Guild, int],
        item: Union[discord.Role, discord.Member, int],
    ) -> bool:
        if isinstance(item, int):
            if isinstance(guild, int):
                guild = self.bot.get_guild(guild)
            combined = guild.members + guild.roles
            item = discord.utils.get(combined, id=item)
            if not item:
                return False
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        config = await self.get_config(guild_id)
        if not config:
            return False
        if isinstance(item, discord.Role):
            blacklist_type = "blacklisted_roles"
        else:
            blacklist_type = "blacklisted_users"
        blacklist: list = config.get(blacklist_type)
        if item.id in blacklist:
            return False
        blacklist.append(item.id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    f"UPDATE counting_config SET {blacklist_type}=$1 WHERE guild_id=$2",
                    blacklist,
                    guild_id,
                )
                return True

    async def blacklist_remove(
        self,
        guild: Union[discord.Guild, int],
        item: Union[discord.Role, discord.Member, int],
    ) -> bool:
        if isinstance(item, int):
            if isinstance(guild, int):
                guild = self.bot.get_guild(guild)
            combined = guild.members + guild.roles
            item = discord.utils.get(combined, id=item)
            if not item:
                return False
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        config = await self.get_config(guild_id)
        if not config:
            return False
        if isinstance(item, discord.Role):
            blacklist_type = "blacklisted_roles"
        else:
            blacklist_type = "blacklisted_users"
        blacklist: list = config.get(blacklist_type)
        if item.id not in blacklist:
            return False
        blacklist.remove(item.id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    f"UPDATE counting_config SET {blacklist_type}=$1 WHERE guild_id=$2",
                    blacklist,
                    guild_id,
                )
                return True

    async def add_number(
        self, guild: Union[discord.Guild, int], user: Union[discord.Member, int]
    ):
        guild_id = guild.id if isinstance(guild, discord.Guild) else guild
        user_id = user.id if isinstance(user, discord.Member) else user
        config = await self.get_config(guild_id)
        if not config:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE counting_config SET num=num+1, user_id=$1 WHERE guild_id=$2",
                    user_id,
                    guild_id,
                )
                return True
