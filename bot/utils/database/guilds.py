from ._core import CoreDB
#Local Imports

class GuildsDB(CoreDB):

    async def get_staff_roles(self, guild_id: int):
        async with self.pool.acquire() as conn:
            roles = dict(await conn.fetchrow("SELECT moderator_roles, admin_roles FROM guilds WHERE guild_id=$1", guild_id))
            return roles

    async def get_staff(self, guild_id: int):
        async with self.pool.acquire() as conn:
            users = dict(await conn.fetchrow("SELECT moderator_users, admin_users FROM guilds WHERE guild_id=$1", guild_id))
            return users