from discord import Interaction, Member, Webhook
from discord.app_commands import command, describe
#Discord Imports

import datetime
#Regular Imports

from utils import *
#Local Imports

class Stats(ExultCog):

    @command(name="modstats", description="View moderation stats for a given member.")
    @describe(member="The member you want to view moderation stats for.")
    async def modstats_slash(self, itr: Interaction, member: Member=None):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: Webhook = itr.followup
        member = member or itr.user

        cases = await CasesDB(bot).get_cases_by_moderator(itr.guild.id, member.id)
        
        if not cases:
            embed = embed_builder(title=f"Member {member} has no mod stats to display.")
            await followup.send(embed=embed)

        last_7 = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        last_28 = datetime.datetime.utcnow() - datetime.timedelta(days=28)

        mutes_7 = [case for case in cases if case["case_type"] in ["Mute", "Tempmute"] and bot.time(case["created_at"]) > bot.time(last_7)]
        mutes_28 = [case for case in cases if case["case_type"] in ["Mute", "Tempmute"] and bot.time(case["created_at"]) > bot.time(last_28)]
        mutes_all = [case for case in cases if case["case_type"] in ["Mute", "Tempmute"]]
        kicks_7 = [case for case in cases if case["case_type"] == "Kick" and bot.time(case["created_at"]) > bot.time(last_7)]
        kicks_28 = [case for case in cases if case["case_type"] == "Kick" and bot.time(case["created_at"]) > bot.time(last_28)]
        kicks_all = [case for case in cases if case["case_type"] == "Kick"]
        bans_7 = [case for case in cases if case["case_type"] == "Ban" and bot.time(case["created_at"]) > bot.time(last_7)]
        bans_28 = [case for case in cases if case["case_type"] == "Ban" and bot.time(case["created_at"]) > bot.time(last_28)]
        bans_all = [case for case in cases if case["case_type"] == "Ban"]
        warns_7 = [case for case in cases if case["case_type"] == "Warn" and bot.time(case["created_at"]) > bot.time(last_7)]
        warns_28 = [case for case in cases if case["case_type"] == "Warn" and bot.time(case["created_at"]) > bot.time(last_28)]
        warns_all = [case for case in cases if case["case_type"] == "Warn"]

        embed = embed_builder(title=f"{member}'s Moderation Stats",
                              author=[bot.try_asset(member.display_avatar, itr.guild.icon), member],
                              thumbnail=bot.try_asset(member.display_avatar, itr.guild.icon),
                              fields=[["Mutes (Last 7 days)", f"{len(mutes_7)}", True], ["Mutes (Last Month)", f"{len(mutes_28)}", True], ["Mutes (All Time)", f"{len(mutes_all)}", True],
                                      ["Kicks (Last 7 days)", f"{len(kicks_7)}", True], ["Kicks (Last Month)", f"{len(kicks_28)}", True], ["Kicks (All Time)", f"{len(kicks_all)}", True],
                                      ["Bans (Last 7 days)", f"{len(bans_7)}", True], ["Bans (Last Month)", f"{len(bans_28)}", True], ["Bans (All Time)", f"{len(bans_all)}", True],
                                      ["Warns (Last 7 days)", f"{len(warns_7)}", True], ["Warns (Last Month)", f"{len(warns_28)}", True], ["Warns (All Time)", f"{len(warns_all)}", True]])

        await followup.send(embed=embed)

