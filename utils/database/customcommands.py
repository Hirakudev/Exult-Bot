from ._core import CoreDB


class CustomCommandsDB(CoreDB):
    async def get_command(self, *, guild_id: int, name: str):
        async with self.pool.acquire() as conn:
            command = await conn.fetchrow(
                "SELECT * FROM custom_commands WHERE guild_id=$1 AND command_name=$2",
                guild_id,
                name,
            )
            if command:
                return dict(command)
            return None

    async def get_commands(self, *, guild_id: int):
        async with self.pool.acquire() as conn:
            commands = await conn.fetch(
                "SELECT * FROM custom_commands WHERE guild_id=$1", guild_id
            )
            if commands:
                return [dict(command) for command in commands]
            return None

    async def add_command(
        self, *, guild_id: int, name: str, response: str, added_by: int
    ):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO custom_commands VALUES (guild_id, command_name, command_text, command_creator "
                "VALUES ($1, $2, $3, $4)",
                guild_id,
                name,
                response,
                added_by,
            )

    async def edit_name(self, *, guild_id: int, name: str, new_name: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE custom_commands SET command_name=$1 WHERE guild_id=$2 AND command_name=$3",
                new_name,
                guild_id,
                name,
            )

    async def edit_response(self, *, guild_id: int, name: str, new_response):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE custom_commands SET command_text=$1 WHERE guild_id=$2 AND command_name=$3",
                new_response,
                guild_id,
                name,
            )

    async def delete_command(self, *, guild_id: int, name: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM custom_commands WHERE guild_id=$1 AND command_name=$2",
                guild_id,
                name,
            )
