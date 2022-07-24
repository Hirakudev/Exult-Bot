import discord
from discord import app_commands
from discord.ext import commands
from typing import Any, TYPE_CHECKING, List, Optional
from utils import *

if TYPE_CHECKING:
    from bot import PartnerBot


class TicketsConfig(commands.Cog):
    def __init__(self, bot: "PartnerBot"):
        self.bot = bot

    ticket_base = app_commands.Group(
        name="ticket",
        description="Ticket Handler",
        default_permissions=discord.Permissions(manage_guild=True),
    )
    panel_group = app_commands.Group(
        name="panel", description="Ticket Panel Handler", parent=ticket_base
    )

    db: Optional["TicketsDB"] = None

    async def cog_load(self):
        self.db = TicketsDB(self.bot)
        panels = await self.db.get_panels(self.bot._guild)
        for panel in panels:
            self.bot.ticketpanels.append(panel)

    async def cog_unload(self):
        await self.db.upload_cache(self.bot.ticketpanels)

    @panel_group.command(name="create", description="Create a Ticket Panel!")
    async def ticket_panel_create(self, itr: Interaction):
        embed = embed_builder(
            title=f"Ticket Panel Creator",
            description=f"Press the `✅ Confirm` Button to Finish!",
            fields=[
                [
                    "Panel Name:",
                    "`Not Configured`",
                    True,
                ],
                ["Channel:", "`Not Configured.`", True],
                [
                    "Category:",
                    "`Not Configured`",
                    True,
                ],
                [
                    "Edit Embed:",
                    "The buttons found on the 2nd row are what allow you to customise the message and embed corresponding to this ticket panel. You can edit each individual component of the message using those buttons.",
                    False,
                ],
            ],
        )
        view = CreatePanelView()
        await itr.response.send_message(embed=embed, view=view)

    @panel_group.command(name="edit", description="Edit a Ticket Panel!")
    async def ticket_panel_edit(self, itr: Interaction, panel_name: str):
        selected_panel = None
        for panel in itr.client.ticketpanels:
            if panel.get("panel_name").lower() == panel_name.lower():
                if panel.get("guild_id") == itr.guild.id:
                    selected_panel = panel
        if not selected_panel:
            await itr.response.send_message(
                f"`{panel_name}` is not an existing Ticket Panel!"
            )

        panel_name = selected_panel.get("panel_name")
        panel_category_id = selected_panel.get("ticket_category")
        panel_category = itr.guild.get_channel(panel_category_id) or "Deleted Category"
        _ticket_types: List[dict] = selected_panel.get("views")
        ticket_types = []
        if _ticket_types:
            for ticket_type in _ticket_types:
                ticket_types.append(ticket_type.get("ticket_label"))
            ticket_types = "\n".join(ticket_types)
        else:
            ticket_types = "`No Ticket Types Created`"
        embed = embed_builder(
            title=f"Ticket Panel Editor | {panel_name}",
            description=f"Press the `✅ Confirm` Button to Confirm your Changes!",
            fields=[
                ["Panel Name:", f"`{panel_name}`", True],
                ["Category:", f"`{panel_category}`", True],
                ["Ticket Types:", ticket_types, True],
            ],
        )
        view = EditPanelView(selected_panel)
        await itr.response.send_message(embed=embed, view=view)

    @ticket_panel_edit.autocomplete("panel_name")
    async def ticket_panel_edit_autocomplete(self, itr: Interaction, current: str):
        panels = []
        for panel in self.bot.ticketpanels:
            panels.append(panel.get("panel_name"))
        if panels:
            return [
                app_commands.Choice(name=p, value=p)
                for p in panels
                if current.lower() in p.lower()
            ]
