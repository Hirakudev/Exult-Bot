from discord import Guild, Interaction, Member, Webhook
from discord.app_commands import describe, Group
from discord.utils import as_chunks, format_dt
# Discord Imports

import datetime
# Regular Imports

from utils import *
# Local Imports

class Cases(ExultCog):

    cases = Group(name="cases", description="Handle Moderation Cases stored for this server!")
    display = Group(name="display", description="Display all cases for a guild or member", parent=cases)
    clear = Group(name="clear", description="Clear all cases for a guild or member", parent=cases)

    @display.command(name="server", description="Display all cases for this server.")
    @guild_staff(manage_messages=True)
    async def cases_display_server_slash(self, itr: Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: Webhook = itr.followup
        guild: Guild = itr.guild

        _cases = await CasesDB(bot).get_cases_by_guild(guild.id)

        if not _cases:
            return

        formatted_cases: list = as_chunks(_cases, 4)

        embeds = []
        for cases in formatted_cases:
            embed = embed_builder(author=[bot.try_asset(guild.icon), f"Cases for {guild.name}"],
                                  footer=f"Total Cases for {guild.name}: {len(_cases)}")
            for case in cases:
                if not case["last_updated"]:
                    last_updated = f"__Case Updated:__ {format_dt(bot.time(case['created_at']), style='R')}"
                elif case["last_updated"]:
                    last_updated = f"__Case Updated:__ {format_dt(bot.time(case['last_updated']), style='R')}"
                if not case["expires"]:
                    case_activity = "__Case Activity:__ `Completed`"
                elif case["expires"]:
                    is_active = bot.time(datetime.datetime.utcnow()) < bot.time(case["expires"])
                    case_activity = "__Case Activity:__ `Completed`" if not is_active else \
                                   f"__Case Activity:__ `Expires in` {format_dt(bot.time(case['expires']), style='R')}"
                value = f"""
                        __Case Type:__ `{case['case_type']}`
                        __Case Offender:__ {case['user_id']}
                        __Case Moderator:__ {case['moderator_id']}
                        __Case Reason:__ `{case['reason']}`
                        __Case Created:__ {format_dt(bot.time(case['created_at']), style='R')}
                        {last_updated}
                        {case_activity}"""
                embed.add_field(name=f"Case ID: {case['case_id']}", value=value, inline=False)
            embeds.append(embed)
        if len(embeds) > 1:
            view = Paginator(pages=embeds)
            await followup.send(embed=embeds[0], view=view)
        else:
            await followup.send(embed=embeds[0])

    @display.command(name="member", description="Display moderation cases for a member in the current server.")
    @describe(member="The member you want to view moderation cases for.")
    @guild_staff(manage_messages=True)
    async def cases_display_member_slash(self, itr: Interaction, member: Member=None):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: Webhook = itr.followup
        member = member or itr.user
        guild = itr.guild

        _cases = await CasesDB(bot).get_cases_by_member(guild.id, member.id)

        if not _cases:
            return

        formatted_cases: list = as_chunks(_cases, 5)

        embeds = []
        for cases in formatted_cases:
            embed = embed_builder(author=[bot.try_asset(member.display_avatar, guild.icon), f"Cases for {member}"],
                                  footer=f"Total Cases for {member}: {len(_cases)}")
            for case in cases:
                if not case["last_updated"]:
                    last_updated = f"__Case Updated:__ {format_dt(bot.time(case['created_at']), style='R')}"
                elif case["last_updated"]:
                    last_updated = f"__Case Updated:__ {format_dt(bot.time(case['last_updated']), style='R')}"
                if not case["expires"]:
                    case_activity = "__Case Activity:__ `Completed`"
                elif case["expires"]:
                    is_active = bot.time(datetime.datetime.utcnow()) < bot.time(case["expires"])
                    case_activity = "__Case Activity:__ `Completed`" if not is_active else \
                                   f"__Case Activity:__ `Expires in` {format_dt(bot.time(case['expires']), style='R')}"
                value = f"""
                        __Case Type:__ `{case['case_type']}`
                        __Case Moderator:__ {case['moderator_id']}
                        __Case Reason:__ `{case['reason']}`
                        __Case Created:__ {format_dt(bot.time(case['created_at']), style='R')}
                        {last_updated}
                        {case_activity}"""
                embed.add_field(name=f"Case ID: {case['case_id']}", value=value, inline=False)
            embeds.append(embed)
        if len(embeds) > 1:
            view = Paginator(pages=embeds)
            await followup.send(embed=embeds[0], view=view)
        else:
            await followup.send(embed=embeds[0])

    @clear.command(name="server", description="Clear all moderation cases for the current server.")
    @guild_staff(admin=True)
    async def cases_clear_server_slash(self, itr: Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: Webhook = itr.followup
        guild: Guild = itr.guild

        cases = await CasesDB(bot).delete_cases_for_guild(guild.id)
        if not cases:
            return

        embed = embed_builder(title=f"Deleted all cases for {guild.name}", description=f"Total Cases: `{cases}`")
        await followup.send(embed=embed)

    @clear.command(name="member", description="Clear all moderation cases for a member in the current server.")
    @describe(member="The member you want to clear moderation cases for.")
    @guild_staff(admin=True)
    @moderation(self_action=True)
    async def cases_clear_server_slash(self, itr: Interaction, member: Member):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: Webhook = itr.followup
        guild: Guild = itr.guild

        cases = await CasesDB(bot).delete_cases_for_member(guild.id, member.id)
        if not cases:
            return

        embed = embed_builder(title=f"Deleted all cases for {member}", description=f"Total Cases: `{cases}`")
        await followup.send(embed=embed)