import discord
from discord import app_commands

# Discord Imports

import datetime

# Regular Imports

from bot import ExultBot
from utils import *

# Local Imports


class Case(ExultCog):

    case = app_commands.Group(
        name="case", description="Handle Moderation Cases stored for this server!"
    )

    @case.command(
        name="display",
        description="Display information on a Moderation Case from this server.",
    )
    @app_commands.describe(case_id="The ID of the case you want to view.")
    @guild_staff(manage_messages=True)
    async def case_display_slash(self, itr: discord.Interaction, case_id: int):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        guild = itr.guild

        case = await CasesDB(bot).get_case(guild.id, case_id)

        if not case:
            return

        embed = embed_builder(
            author=[bot.try_asset(guild.icon), f"Cases for {guild.name}"]
        )
        if not case["last_updated"]:
            last_updated = f"__Case Updated:__ {discord.utils.format_dt(bot.time(case['created_at']), style='R')}"
        elif case["last_updated"]:
            last_updated = f"__Case Updated:__ {discord.utils.format_dt(bot.time(case['last_updated']), style='R')}"
        if not case["expires"]:
            case_activity = "__Case Activity:__ `Completed`"
        elif case["expires"]:
            is_active = bot.time(datetime.datetime.utcnow()) < bot.time(case["expires"])
            case_activity = (
                "__Case Activity:__ `Completed`"
                if not is_active
                else f"__Case Activity:__ `Expires in` {discord.utils.format_dt(bot.time(case['expires']), style='R')}"
            )
        value = f"""
                __Case Type:__ `{case['case_type']}`
                __Case Offender:__ {case['user_id']}
                __Case Moderator:__ {case['moderator_id']}
                __Case Reason:__ `{case['reason']}`
                __Case Created:__ {discord.utils.format_dt(bot.time(case['created_at']), style='R')}
                {last_updated}
                {case_activity}"""
        embed.add_field(name=f"Case ID: {case['case_id']}", value=value, inline=False)

        await followup.send(embed=embed)

    @case.command(
        name="delete", description="Delete a Moderation Case from this server."
    )
    @app_commands.describe(case_id="The ID of the case you want to delete.")
    @guild_staff(manage_messages=True)
    @moderation(self_action=True)
    async def case_delete_slash(self, itr: discord.Interaction, case_id: int):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        guild = itr.guild

        case = await CasesDB(bot).delete_case(guild.id, case_id)
        if not case:
            return

        embed = embed_builder(title=f"Successfully deleted case {case_id}")
        await followup.send(embed=embed)

    @case.command(name="edit", description="Edit a Moderation Case from this server.")
    @app_commands.describe(case_id="The ID of the case you want to edit.")
    @guild_staff(manage_messages=True)
    @moderation(self_action=True)
    async def case_edit_slash(self, itr: discord.Interaction, case_id: int):
        bot: ExultBot = itr.client
        guild = itr.guild

        case = await CasesDB(bot).get_case(guild.id, case_id)
        if not case:
            return

        data = {"db": CasesDB, "embed": embed_builder}
        view = CaseEditModal(bot, case, data)
        await itr.response.send_modal(view)
