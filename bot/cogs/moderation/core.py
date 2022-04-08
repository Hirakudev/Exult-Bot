from discord import Interaction, Member, User, Webhook
from discord.app_commands import command, describe
from discord.utils import format_dt, utcnow
#Discord Imports

import datetime
#Regular Imports

from utils import *
#Local Imports

class Core(ExultCog):

    @command(name="ban", description="Ban a member from the server.")
    @describe(member="A member you want to ban.", reason="The reason for the ban.")
    @guild_staff(ban_members=True)
    @moderation(self_action=True)
    async def ban_slash(self, itr: Interaction, member: Member, reason: str="Unspecified"):
        bot: ExultBot = itr.client
        await itr.response.defer()
        followup: Webhook = itr.followup

        embed = embed_builder(
            title=f"You have been banned from {itr.guild.name}",
            description=f"**Reason:** {reason}\n**Banned:** {format_dt(utcnow(), style='R')}",
            thumbnail=bot.try_asset(itr.guild.icon)
        )

        await bot.try_send(member, embed=embed)
        #await itr.guild.ban(member, reason=reason)
        case = await CasesDB(self.bot).add_case("Ban", itr.guild.id, member.id, itr.user.id, reason, utcnow(), None, return_case=True)

        log_embed = embed_builder(
            author=[bot.try_asset(member.avatar, itr.guild.icon), f"Case {case['num']} | Ban"],
            thumbnail=bot.try_asset(member.avatar, itr.guild.icon),
            fields=[["User:", member, False], ["Moderator:", itr.user.mention], ["Reason:", reason, False]],
            footer=f"Offender ID: {member.id}"
        )

        await followup.send(embed=log_embed)

        if case["log_channel"]:
            channel = bot.get_channel(case["log_channel"])
            log_embed.add_field(name="Banned:", value=f"{format_dt(utcnow(), style='R')}", inline=False)
            await channel.send(embed=log_embed)

    @command(name="kick", description="Kick a member from the server.")
    @describe(member="A member you want to kick.", reason="The reason for the kick.")
    @guild_staff(kick_members=True)
    @moderation(self_action=True)
    async def kick_slash(self, itr: Interaction, member: Member, reason: str="Unspecified"):
        bot: ExultBot = itr.client
        await itr.response.defer()
        followup: Webhook = itr.followup

        embed = embed_builder(
            title=f"You have been kicked from {itr.guild.name}",
            description=f"**Reason:** {reason}\n**Kicked:** {format_dt(utcnow(), style='R')}",
            thumbnail=bot.try_asset(itr.guild.icon)
        )

        await bot.try_send(member, embed=embed)
        #await itr.guild.kick(member, reason=reason)
        case = await CasesDB(self.bot).add_case("Kick", itr.guild.id, member.id, itr.user.id, reason, utcnow(), None, return_case=True)

        log_embed = embed_builder(
            author=[bot.try_asset(member.avatar, itr.guild.icon), f"Case {case['num']} | Kick"],
            thumbnail=bot.try_asset(member.avatar, itr.guild.icon),
            fields=[["User:", member, False], ["Moderator:", itr.user.mention], ["Reason:", reason, False]],
            footer=f"Offender ID: {member.id}"
        )

        await followup.send(embed=log_embed)

        if case["log_channel"]:
            channel = bot.get_channel(case["log_channel"])
            log_embed.add_field(name="Kicked:", value=f"{format_dt(utcnow(), style='R')}", inline=False)
            await channel.send(embed=log_embed)

    @command(name="unban", description="Unban a user from the server.")
    @describe(user="A user you want to unban.", reason="The reason for the unban.")
    @guild_staff(ban_members=True)
    @moderation(self_action=True)
    async def unban_slash(self, itr: Interaction, user: User, reason: str="Unspecified"):
        bot: ExultBot = itr.client
        await itr.response.defer()
        followup: Webhook = itr.followup

        await itr.guild.unban(user, reason=reason)

        embed = embed_builder(
            title=f"You have been unbanned from {itr.guild.name}",
            description=f"**Reason:** {reason}\n**Unbanned:** {format_dt(utcnow(), 'R')}",
            thumbnail=bot.try_asset(itr.guild.icon)
        )

        await bot.try_send(user, embed=embed)

        case = await CasesDB(bot).add_case("Unban", itr.guild.id, user.id, itr.user.id, reason, utcnow(), None, return_case=True)

        log_embed = embed_builder(
            author=[bot.try_asset(user.avatar, itr.guild.icon), f"Case {case['num']} | Unban"],
            thumbnail=bot.try_asset(user.avatar, itr.guild.icon),
            fields=[["User:", user, False], ["Moderator:", itr.user.mention], ["Reason:", reason, False]],
            footer=f"Offender ID: {user.id}"
        )

        await followup.send(embed=log_embed)

        if case["log_channel"]:
            channel = bot.get_channel(case["log_channel"])
            log_embed.add_field(name="Unbanned:", value=f"{format_dt(utcnow(), style='R')}", inline=False)
            await channel.send(embed=log_embed)

    @command(name="mute", description="Mute a member in the server. (Uses Timeout, not Role)")
    @describe(member="A member you want to mute.", reason="The reason for the mute.")
    @guild_staff(moderate_members=True)
    @moderation(self_action=True)
    async def mute_slash(self, itr: Interaction, member: Member, reason: str="Unspecified"):
        if member.timed_out_until:
            return
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: Webhook = itr.followup
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=28)
        expires = bot.time(expires)

        await member.timeout(expires, reason=reason)

        embed = embed_builder(
            title=f"You have been muted in {itr.guild.name}",
            description=f"**Reason:** {reason}\n**Muted:** {format_dt(utcnow(), 'R')}\n**Muted Until:** {format_dt(expires, style='R')}",
            thumbnail=bot.try_asset(itr.guild.icon)
        )

        await bot.try_send(member, embed=embed)

        case = await CasesDB(bot).add_case("Mute", itr.guild.id, member.id, itr.user.id, reason, utcnow(), expires, return_case=True)

        log_embed = embed_builder(
            author=[bot.try_asset(member.avatar, itr.guild.icon), f"Case {case['num']} | Mute"],
            thumbnail=bot.try_asset(member.avatar, itr.guild.icon),
            fields=[["User:", member, False], ["Moderator:", itr.user.mention], ["Reason:", reason, False], ["Expires:", format_dt(expires, 'R'), False]],
            footer=f"Offender ID: {member.id} | Indefinite mute is limited to 28 days maximum"
        )

        await followup.send(embed=log_embed)

        if case["log_channel"]:
            channel = bot.get_channel(case["log_channel"])
            log_embed.add_field(name="Muted:", value=f"{format_dt(utcnow(), style='R')}", inline=False)
            await channel.send(embed=log_embed)

    @command(name="tempmute", description="Temporarily mute a member in the server. (Uses Timeout, not Role)")
    @describe(member="A member you want to mute.", 
              duration="How long you would like the mute to last",
              reason="The reason for the mute.")
    @guild_staff(moderate_members=True)
    @moderation(self_action=True)
    async def tempmute_slash(self, itr: Interaction, member: Member, duration: str, reason: str="Unspecified"):
        if member.timed_out_until:
            return
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: Webhook = itr.followup
        expires = time_handler(duration)

        await member.timeout(expires, reason=reason)

        embed = embed_builder(
            title=f"You have been muted in {itr.guild.name}",
            description=f"**Reason:** {reason}\n**Muted:** {format_dt(utcnow(), 'R')}\n**Muted Until:** {format_dt(expires, style='R')}",
            thumbnail=bot.try_asset(itr.guild.icon)
        )

        await bot.try_send(member, embed=embed)

        case = await CasesDB(bot).add_case("Tempmute", itr.guild.id, member.id, itr.user.id, reason, utcnow(), expires, return_case=True)

        log_embed = embed_builder(
            author=[bot.try_asset(member.avatar, itr.guild.icon), f"Case {case['num']} | Tempmute"],
            thumbnail=bot.try_asset(member.avatar, itr.guild.icon),
            fields=[["User:", member, False], ["Moderator:", itr.user.mention], ["Reason:", reason, False], ["Expires:", format_dt(expires, 'R'), False]],
            footer=f"Offender ID: {member.id}"
        )

        await followup.send(embed=log_embed)

        if case["log_channel"]:
            channel = bot.get_channel(case["log_channel"])
            log_embed.add_field(name="Muted:", value=f"{format_dt(utcnow(), style='R')}", inline=False)
            await channel.send(embed=log_embed)


    @command(name="unmute", description="Unmute a member in the server. (Uses Timeout, not Role)")
    @describe(member="A member you want to unmute.", reason="The reason for the unmute.")
    @guild_staff(moderate_members=True)
    @moderation(self_action=True)
    async def unmute_slash(self, itr: Interaction, member: Member, reason: str="Unspecified"):
        if not member.timed_out_until:
            return
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: Webhook = itr.followup

        await member.timeout(None, reason=reason)

        embed = embed_builder(
            title=f"You have been unmuted in {itr.guild.name}",
            description=f"**Reason:** {reason}\n**Unmuted:** {format_dt(utcnow(), 'R')}",
            thumbnail=bot.try_asset(itr.guild.icon)
        )

        await bot.try_send(member, embed=embed)

        case = await CasesDB(bot).add_case("Unmute", itr.guild.id, member.id, itr.user.id, reason, utcnow(), None, return_case=True)

        log_embed = embed_builder(
            author=[bot.try_asset(member.avatar, itr.guild.icon), f"Case {case['num']} | Unmute"],
            thumbnail=bot.try_asset(member.avatar, itr.guild.icon),
            fields=[["User:", member, False], ["Moderator:", itr.user.mention], ["Reason:", reason, False]],
            footer=f"Offender ID: {member.id}"
        )

        await followup.send(embed=log_embed)

        if case["log_channel"]:
            channel = bot.get_channel(case["log_channel"])
            log_embed.add_field(name="Unmuted:", value=f"{format_dt(utcnow(), style='R')}", inline=False)
            await channel.send(embed=log_embed)