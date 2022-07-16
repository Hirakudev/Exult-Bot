from typing import Any, Dict, List
from uuid import UUID
import discord

# Discord Imports

import datetime
import asyncpg

# Regular Imports

from .logs import LogsDB
from ._core import CoreDB

# Local Imports


class CasesDB(CoreDB):
    def prepare_time(self, time: datetime.datetime = None):
        if time:
            return time.replace(tzinfo=None)
        return None

    async def add_case(
        self,
        case_type: str,
        guild_id: int,
        user_id: int,
        moderator_id: int,
        reason: str,
        created_at: datetime.datetime,
        expires: datetime.datetime = None,
        **kwargs
    ):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO cases (case_type, guild_id, user_id, moderator_id, reason, created_at, expires) VALUES "
                    "($1, $2, $3, $4, $5, $6, $7)",
                    case_type,
                    guild_id,
                    user_id,
                    moderator_id,
                    reason,
                    self.prepare_time(created_at),
                    self.prepare_time(expires),
                )
                if kwargs.get("return_case") == True:
                    cases = await conn.fetchval(
                        "SELECT COUNT(*) FROM cases WHERE guild_id=$1", guild_id
                    )
                    log = await LogsDB(self.bot).get_config(guild_id)['moderation_logs']
                    return {"num": cases, "log_channel": log}

    async def get_case(self, guild_id: int, case_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                case = await conn.fetchrow(
                    "SELECT * FROM cases WHERE case_id=$1", case_id
                )
                if case["guild_id"] == guild_id:
                    return dict(case)
        return False

    async def fetch_case(self, case_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                case = await conn.fetchrow(
                    "SELECT * FROM cases WHERE case_id=$1", case_id
                )
                if case:
                    return dict(case)
        return None

    async def update_case(self, case_id: int, reason: str):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                case = await self.check_case_exists(case_id)
                if case:
                    await conn.execute(
                        "UPDATE cases SET reason=$1 WHERE case_id=$2", reason, case_id
                    )
                    await conn.execute(
                        "UPDATE cases SET last_updated=$1 WHERE case_id=$2",
                        self.prepare_time(discord.utils.utcnow()),
                        case_id,
                    )
                    return True
        return False

    async def delete_case(self, case_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                case = await self.check_case_exists(case_id)
                if case:
                    await conn.execute("DELETE FROM cases WHERE case_id=$1", case_id)
                    return True
        return False

    async def get_cases_by_moderator(self, guild_id: int, moderator_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                cases = await conn.fetch(
                    "SELECT * FROM cases WHERE guild_id=$1 AND moderator_id=$2",
                    guild_id,
                    moderator_id,
                )
                if len(cases):
                    return [dict(case) for case in cases]
        return None

    async def get_cases_by_member(self, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                cases = await conn.fetch(
                    "SELECT * FROM cases WHERE guild_id=$1 AND user_id=$2",
                    guild_id,
                    user_id,
                )
                if len(cases):
                    return [dict(case) for case in cases]
        return None

    async def get_cases_by_guild(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                cases = await conn.fetch(
                    "SELECT * FROM cases WHERE guild_id=$1", guild_id
                )
                if len(cases):
                    return [dict(case) for case in cases]
        return None

    async def delete_cases_for_guild(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                cases = self.get_cases_by_guild(guild_id)
                await conn.execute("DELETE FROM cases WHERE guild_id=$1", guild_id)
                if len(cases):
                    return len(cases)
        return None

    async def delete_cases_for_member(self, guild_id: int, user_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                cases = await self.get_cases_by_member(guild_id, user_id)
                await conn.execute(
                    "DELETE FROM cases WHERE guild_id=$1 AND user_id=$2",
                    guild_id,
                    user_id,
                )
                if len(cases):
                    return len(cases)
        return None

    async def check_case_exists(self, case_id:UUID):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                case = await self.fetch_case(case_id)
                if not case:
                    return False
                return case
