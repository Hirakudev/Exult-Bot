import discord

from typing import Union

from ._core import CoreDB


class EmotionDB(CoreDB):
    async def get_marriage(
        self, user_one: Union[discord.Member, int], user_two: Union[discord.Member, int]
    ):
        user_one_id = user_one.id if isinstance(user_one, discord.Member) else user_one
        user_two_id = user_two.id if isinstance(user_two, discord.Member) else user_two
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                couple = await conn.fetchrow(
                    "SELECT * FROM marriages WHERE user_one=$1 AND user_two=$2 OR user_one=$2 AND user_two=$1",
                    user_one_id,
                    user_two_id,
                )
                if couple:
                    return dict(couple)
                return None

    async def marry(self, user_one: int, user_two: int):
        user_one_id = user_one.id if isinstance(user_one, discord.Member) else user_one
        user_two_id = user_two.id if isinstance(user_two, discord.Member) else user_two
        couple = await self.get_marriage(user_one_id, user_two_id)
        if couple:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO marriages (user_one, user_two) VALUES ($1, $2)",
                    user_one_id,
                    user_two_id,
                )
                return True

    async def divorce(self, user_one: int, user_two: int):
        user_one_id = user_one.id if isinstance(user_one, discord.Member) else user_one
        user_two_id = user_two.id if isinstance(user_two, discord.Member) else user_two
        couple = await self.get_marriage(user_one_id, user_two_id)
        if not couple:
            return False
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM marriages WHERE user_one=$1 AND user_two=$2 OR user_one=$2 AND user_two=$1",
                    user_one_id,
                    user_two_id,
                )
                return True
