from datetime import datetime
#Regular Imports

from .logs import LogsDB
from ._core import CoreDB
#Local Imports

class CasesDB(CoreDB):

    async def add_case(self, case_type: str, guild_id: int, user_id: int, moderator_id: int, reason: str, created_at: datetime, expires: datetime=None, **kwargs):
        async with self.pool.acquire() as conn:
            expires = None if not expires else expires.replace(tzinfo=None)
            await conn.execute("INSERT INTO cases (case_type, guild_id, user_id, moderator_id, reason, created_at, expires) VALUES " \
                               "($1, $2, $3, $4, $5, $6, $7)", case_type, guild_id, user_id, moderator_id, reason, 
                               created_at.replace(tzinfo=None), expires)
            if kwargs.get("return_case") == True:
                cases = await conn.fetchval("SELECT COUNT(*) FROM cases WHERE guild_id=$1", guild_id)
                log = await LogsDB(self.bot).get_moderation_logs(guild_id)
                return {"num": cases, "log_channel": log}

    async def get_cases_by_moderator(self, guild_id: int, moderator_id: int):
        async with self.pool.acquire() as conn:
            cases = await conn.fetch("SELECT * FROM cases WHERE guild_id=$1 AND moderator_id=$2", guild_id, moderator_id)
            if len(cases):
                return [dict(case) for case in cases]
            return None