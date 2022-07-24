import discord

from ast import literal_eval
from typing import List, Union

from ._core import CoreDB


class TicketsDB(CoreDB):
    async def get_panels(self, guild_id: int):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                _panels = await conn.fetch(
                    "SELECT * FROM ticketpanels WHERE guild_id=$1", guild_id
                )
            if _panels:
                panels = [dict(panel) for panel in _panels]
                for panel in panels:
                    async with conn.transaction():
                        embed = await conn.fetchrow(
                            "SELECT * FROM ticketpanelembeds WHERE guild_id=$1 AND panel_name=$2",
                            panel["guild_id"],
                            panel["panel_name"],
                        )
                        if embed:
                            db_embed = dict(embed)
                            embed = {}
                            title = db_embed.get("panel_name")
                            desc = db_embed.get("embed_description")
                            colour = db_embed.get("embed_colour")
                            thumb = db_embed.get("embed_thumbnail")
                            image = db_embed.get("embed_image")
                            embed["title"] = title
                            embed["description"] = desc if desc else None
                            embed["color"] = colour
                            embed["thumbnail"] = literal_eval(thumb) if thumb else None
                            embed["image"] = literal_eval(image) if image else None
                            embed["type"] = "rich"
                            fmt_embed = discord.Embed.from_dict(embed)
                            if fmt_embed:
                                panel["message_embed"] = fmt_embed.to_dict()
                return [dict(panel) for panel in panels]
            return []

    async def add_panel(
        self,
        guild_id: int,
        *,
        panel_name: str,
        category_id: int,
        message_content: str,
        embed_dict: dict,
        message_id: int,
        views: dict = None,
    ):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO ticketpanels (guild_id, panel_name, ticket_category, message_content, message_embed, message_id, views) VALUES ($1, $2, $3, $4, $5, $6, $7)",
                guild_id,
                panel_name,
                category_id,
                message_content,
                embed_dict,
                message_id,
                views,
            )

    async def update_panel(
        self,
        property: str,
        guild_id: int,
        *,
        panel_name: str,
        new_value: Union[str, int, dict],
    ):
        if property not in [
            "panel_name",
            "ticket_category",
            "message_content",
            "message_embed",
            "message_id",
            "views",
        ]:
            return
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    f"UPDATE ticketpanels SET {property}=$1 WHERE guild_id=$2 AND panel_name=$3",
                    new_value,
                    guild_id,
                    panel_name,
                )

    async def delete_panel(self, guild_id: int, *, panel_name: str):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM ticketpanels WHERE guild_id=$1 AND panel_name=$2",
                    guild_id,
                    panel_name,
                )

    async def upload_cache(self, panels: List[dict]):
        if panels:
            async with self.pool.acquire() as conn:
                for panel in panels:
                    async with conn.transaction():
                        try:
                            columns = [
                                "guild_id",
                                "panel_name",
                                "ticket_category",
                                "message_content",
                                "message_id",
                            ]
                            args = [panel[key] for key in columns]
                            await conn.execute(
                                f"INSERT INTO ticketpanels ({', '.join(columns)}) VALUES ($1, $2, $3, $4, $5) ON CONFLICT DO NOTHING",
                                *args,
                            )
                            embed = panel.get("message_embed")
                            if embed:
                                embed_description = embed.get("description")
                                embed_colour = embed.get("color")
                                embed_thumbnail = embed.get("thumbnail")
                                embed_image = embed.get("image")
                                await conn.execute(
                                    "INSERT INTO ticketpanelembeds (guild_id, panel_name, embed_description, embed_colour, embed_thumbnail, embed_image) VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT DO NOTHING",
                                    args[0],
                                    args[1],
                                    embed_description,
                                    embed_colour,
                                    str(embed_thumbnail),
                                    str(embed_image),
                                )
                        except Exception as e:
                            print(e)
