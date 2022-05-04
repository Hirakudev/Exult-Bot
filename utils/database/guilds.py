from ._core import CoreDB

# Local Imports


class GuildsDB(CoreDB):
    async def add_guild(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO guilds (guild_id) VALUES ($1)", guild_id
                )

    async def remove_guild(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM guilds WHERE guild_id=$1", guild_id)

    async def get_staff_roles(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                roles = await conn.fetchrow(
                    "SELECT moderator_roles, admin_roles FROM guilds WHERE guild_id=$1",
                    guild_id,
                )
                if roles:
                    return dict(roles)
        return None

    async def get_staff(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                users = await conn.fetchrow(
                    "SELECT moderator_users, admin_users FROM guilds WHERE guild_id=$1",
                    guild_id,
                )
                if users:
                    return dict(users)
        return None

    async def add_moderator_role(self, guild_id: int, role_id: int):
        roles = await self.get_staff_roles(guild_id)
        if any(role_id == role for role in roles["moderator_roles"]):
            return False
        roles["moderator_roles"].append(role_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE guilds SET moderator_roles=$1 WHERE guild_id=$2",
                    roles["moderator_roles"],
                    guild_id,
                )
                return True

    async def add_moderator_user(self, guild_id: int, user_id: int):
        users = await self.get_staff(guild_id)
        if any(user_id == user for user in users["moderator_users"]):
            return False
        users["moderator_users"].append(user_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE guilds SET moderator_users=$1 WHERE guild_id=$2",
                    users["moderator_users"],
                    guild_id,
                )
                return True

    async def add_admin_role(self, guild_id: int, role_id: int):
        roles = await self.get_staff_roles(guild_id)
        if any(role_id == role for role in roles["admin_roles"]):
            return False
        roles["admin_roles"].append(role_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE guilds SET admin_roles=$1 WHERE guild_id=$2",
                    roles["admin_roles"],
                    guild_id,
                )
                return True

    async def add_admin_user(self, guild_id: int, user_id: int):
        users = await self.get_staff(guild_id)
        if any(user_id == user for user in users["admin_users"]):
            return False
        users["admin_users"].append(user_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE guilds SET moderator_users=$1 WHERE guild_id=$2",
                    users["admin_users"],
                    guild_id,
                )
                return True

    async def remove_moderator_role(self, guild_id: int, role_id: int):
        roles = await self.get_staff_roles(guild_id)
        if not any(role_id == role for role in roles["moderator_roles"]):
            return False
        roles["moderator_roles"].remove(role_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE guilds SET moderator_roles=$1 WHERE guild_id=$2",
                    roles["moderator_roles"],
                    guild_id,
                )
                return True

    async def remove_moderator_user(self, guild_id: int, user_id: int):
        users = await self.get_staff(guild_id)
        if not any(user_id == user for user in users["moderator_users"]):
            return False
        users["moderator_users"].remove(user_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE guilds SET moderator_users=$1 WHERE guild_id=$2",
                    users["moderator_users"],
                    guild_id,
                )
                return True

    async def remove_admin_role(self, guild_id: int, role_id: int):
        roles = await self.get_staff_roles(guild_id)
        if not any(role_id == role for role in roles["admin_roles"]):
            return False
        roles["admin_roles"].remove(role_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE guilds SET admin_roles=$1 WHERE guild_id=$2",
                    roles["admin_roles"],
                    guild_id,
                )
                return True

    async def remove_admin_user(self, guild_id: int, user_id: int):
        users = await self.get_staff(guild_id)
        if not any(user_id == user for user in users["admin_users"]):
            return False
        users["admin_users"].remove(user_id)
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE guilds SET moderator_users=$1 WHERE guild_id=$2",
                    users["admin_users"],
                    guild_id,
                )
                return True
