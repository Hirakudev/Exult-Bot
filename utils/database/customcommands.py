from typing import List

from ._core import CoreDB
from utils import *


class CustomCommandsDB(CoreDB):
    async def get_commands(self):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                commands = await conn.fetch("SELECT * FROM custom_commands")
        if commands:
            return [dict(command) for command in commands]
        return None

    async def upload_commands(self, commands):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM custom_commands")
                for cmd_name in commands:
                    cmd = commands[cmd_name]
                    await conn.execute(
                        "INSERT INTO custom_commands "
                        "(guild_id, command_name, command_text, command_creator, created_at) "
                        "VALUES ($1, $2, $3, $4, $5)",
                        cmd.get("guild_id"),
                        cmd.get("command_name"),
                        cmd.get("command_text"),
                        cmd.get("command_creator"),
                        cmd.get("created_id"),
                    )
