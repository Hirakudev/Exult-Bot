import discord
from discord.ext import commands

import datetime
from typing import Union

from bot import ExultBot
from utils import *


class Loggers(commands.Cog):
    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db = LogsDB(self.bot)

    guild_channels = Union[
        discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel
    ]
    ticks = {
        True: "<a:check:971592474583773264>",
        False: "<a:cross:971592605563506688>",
        None: "<:neutral:971594400297812049>",
    }

    async def get_webhook(
        self, channel: discord.TextChannel, log_type: str
    ) -> discord.Webhook:
        webhooks = await channel.webhooks()
        if webhooks:
            for hook in webhooks:
                if hook.token:
                    if hook.name == log_type:
                        return hook
        hook = await channel.create_webhook(name=log_type)
        return hook

    @commands.Cog.listener(name="on_guild_channel_delete")
    async def logs_channel_delete(self, channel: guild_channels):
        config = await self.db.get_config(guild_id=channel.guild.id)
        if not config.get("guild_logs"):
            return
        log_channel = self.bot.get_channel(config.get("guild_logs"))
        hook = await self.get_webhook(log_channel, "Server Logs")
        async for log in channel.guild.audit_logs(
            action=discord.AuditLogAction.channel_delete, limit=1
        ):
            user = f"**Deleted By:** {log.user}\n"
        name = f"**Name:** {channel.name}\n"
        category = f"**Category:** {channel.category}\n"
        topic = f"\n**Topic:**```\n{channel.topic}```"
        msg = {
            "title": f"{str(channel.type).title().replace('_', ' ')} Channel Deleted | Log",
            "description": f"{name}{category}{user}{topic}",
        }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_guild_channel_create")
    async def logs_channel_create(self, channel: guild_channels):
        config = await self.db.get_config(guild_id=channel.guild.id)
        if not config.get("guild_logs"):
            return
        log_channel = self.bot.get_channel(config.get("guild_logs"))
        hook = await self.get_webhook(log_channel, "Server Logs")
        async for log in channel.guild.audit_logs(
            action=discord.AuditLogAction.channel_create, limit=1
        ):
            user = f"**Created By:** {log.user}\n"
        name = f"**Name:** {channel.name}\n"
        mention = f"**Mention:** {channel.mention}\n"
        category = f"**Category:** {channel.category}\n"
        msg = {
            "title": f"{str(channel.type).title().replace('_', ' ')} Channel Created | Log",
            "description": f"{name}{mention}{category}{user}",
        }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_guild_channel_update")
    async def logs_channel_update(self, before: guild_channels, after: guild_channels):
        config = await self.db.get_config(guild_id=after.guild.id)
        if not config.get("guild_logs"):
            return
        log_channel = self.bot.get_channel(config.get("guild_logs"))
        hook = await self.get_webhook(log_channel, "Server Logs")
        async for log in after.guild.audit_logs(
            action=discord.AuditLogAction.channel_update, limit=1
        ):
            user = f"**Updated By:** {log.user}\n"
        if before.name != after.name:
            msg = {
                "title": f"Channel Name Updated | Log",
                "description": f"**Channel:** {after.mention}\n**Before:** {before.name}\n**After:** {after.name}{user}",
            }
        elif (
            hasattr(before, "topic")
            and hasattr(after, "topic")
            and before.topic != after.topic
        ):
            msg = {
                "title": "Channel Topic Updated | Log",
                "description": f"**Channel:** {after.mention}\n**Before:** ```\n{discord.utils.remove_markdown(before.topic)}```\n"
                f"**After:** ```\n{discord.utils.remove_markdown(after.topic)}```",
            }
        elif before.overwrites != after.overwrites:
            targets = set.union(
                set(before.overwrites.keys()), set(after.overwrites.keys())
            )
            for target in targets:
                updated_perms = []
                boverwrites = dict(before.overwrites_for(target))
                aoverwrites = dict(after.overwrites_for(target))
                for perm, value in boverwrites.items():
                    if value != aoverwrites[perm]:
                        updated_perms.append(
                            f"{str(perm).replace('guild', 'server').replace('_', ' ').title()}: {self.ticks[value]} ➜ {self.ticks[aoverwrites[perm]]}"
                        )
                if len(updated_perms):
                    nl = "\n"  # To bypass the "Can't have backslash in f-string expression"
                    msg = {
                        "title": "Channel Overwrites Updated | Log",
                        "description": f"**Channel:** {after.mention}\n{user}**Permissions For:** {target.mention}\n**Permission(s) Updated:**\n{f'{nl}'.join(updated_perms)}",
                    }
        if msg:
            embed = embed_builder(
                title=msg.get("title"), description=msg.get("description")
            )
            await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_guild_update")
    async def logs_guild_update(self, before: discord.Guild, after: discord.Guild):
        config = await self.db.get_config(guild_id=after.guild.id)
        if not config.get("guild_logs"):
            return
        log_channel = self.bot.get_channel(config.get("guild_logs"))
        hook = await self.get_webhook(log_channel, "Server Logs")
        async for log in after.audit_logs(
            limit=1, action=discord.AuditLogAction.guild_update
        ):
            user = f"**Updated By:** {log.user}"
        if before.icon != after.icon:
            if not after.icon:
                msg = {"title": "Server Icon Removed | Log", "description": user}
            else:
                msg = {
                    "title": "Server Icon Updated | Log",
                    "description": user,
                    "thumbnail": f"{self.bot.try_asset(after.icon)}",
                }
        elif before.banner != after.banner:
            if not after.banner:
                msg = {"title": "Server Banner Removed | Log", "description": user}
            else:
                msg = {
                    "title": "Server Banner Updated | Log",
                    "description": user,
                    "thumbnail": f"{self.bot.try_asset(after.icon)}",
                }
        elif before.name != after.name:
            msg = {
                "title": "Server Name Updated | Log",
                "description": f"**Before:** {before.name}\n**After:** {after.name}\n{user}",
            }
        elif before.owner != after.owner:
            msg = {
                "title": "Server Owner Updated | Log",
                "description": f"**Before:** {before.owner}\n**After:** {after.owner}",
            }
        if msg:
            embed = embed_builder(
                title=msg.get("title"),
                description=msg.get("description"),
                thumbnail=msg.get("thumbnail"),
            )
            await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_member_join")
    async def logs_member_join(self, member: discord.Member):
        config = await self.db.get_config(guild_id=member.guild.id)
        if not config.get("join_logs"):
            return
        log_channel = self.bot.get_channel(config.get("join_logs"))
        hook = await self.get_webhook(log_channel, "Join Logs")
        name = f"**Member:** {member}\n"
        mention = f"**Mention:** {member.mention}\n"
        created = f"**Account Created:** {discord.utils.format_dt(dt=member.created_at, style='R')}"
        msg = {
            "title": f"Member Joined | Log",
            "description": f"{name}{mention}{created}",
        }
        embed = embed_builder(
            title=msg.get("title"),
            description=msg.get("description"),
            footer=f"Members: {len(member.guild.members)}",
        )
        await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_member_remove")
    async def logs_member_remove(self, member: discord.Member):
        config = await self.db.get_config(guild_id=member.guild.id)
        if not config.get("guild_logs"):
            return
        log_channel = self.bot.get_channel(config.get("join_logs"))
        hook = await self.get_webhook(log_channel, "Join Logs")
        name = f"**Member:** {member}\n"
        mention = f"**Mention:** {member.mention}\n"
        joined = f"**Joined Server:** {discord.utils.format_dt(dt=member.joined_at, style='R')}"
        msg = {"title": f"Member Left | Log", "description": f"{name}{mention}{joined}"}
        embed = embed_builder(
            title=msg.get("title"),
            description=msg.get("description"),
            footer=f"Members: {len(member.guild.members)}",
        )
        await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_member_update")
    async def logs_member_update(self, before: discord.Member, after: discord.Member):
        config = await self.db.get_config(guild_id=self.bot._guild)
        if not config.get("member_logs"):
            return
        log_channel = self.bot.get_channel(config.get("member_logs"))
        hook = await self.get_webhook(log_channel, "Member Logs")
        if before.guild_avatar != after.guild_avatar:
            if not after.guild_avatar:
                msg = {
                    "title": "Member Server Avatar Removed | Log",
                    "description": f"**User:** {after}",
                    "thumbnail": self.bot.try_asset(
                        after.display_avatar, after.default_avatar
                    ),
                }
            else:
                msg = {
                    "title": "Member Server Avatar Updated | Log",
                    "description": f"**User:** {after}",
                    "thumbnail": self.bot.try_asset(
                        after.guild_avatar, after.display_avatar
                    ),
                }
        elif before.nick != after.nick:
            time = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
            logs = [
                log
                async for log in after.guild.audit_logs(
                    limit=1, after=time, action=discord.AuditLogAction.member_update
                )
                if log.user != log.target
            ]
            user = f"\n**Updated By:** {logs[0].user}" if len(logs) else ""
            if not after.nick:
                msg = {
                    "title": "Member Server Nickname Removed | Log",
                    "description": f"**User:** {after}{user}",
                }
            else:
                msg = {
                    "title": "Member Server Nickname Updated | Log",
                    "description": f"**User:** {after}\n**Nick Before:** {before.nick}\n**Nick After:** {after.nick}{user}",
                }
        elif before.roles != after.roles:
            added = set(after.roles) - set(before.roles)
            removed = set(before.roles) - set(after.roles)
            add = False
            if added:
                added = f"**Added:** {', '.join([r.mention for r in added])}\n"
                add = True
            else:
                added = ""
            if removed:
                removed = f"**Removed:** {', '.join([r.mention for r in removed])}"
                add = True
            else:
                removed = ""
            if add:
                msg = {
                    "title": "Member Roles Updated | Log",
                    "description": f"{added}{removed}",
                }
        if msg:
            embed = embed_builder(
                title=msg.get("title"),
                description=msg.get("description"),
                thumbnail=msg.get("thumbnail"),
            )
            await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_user_update")
    async def logs_user_update(self, before: discord.User, after: discord.User):
        config = await self.db.get_config(guild_id=self.bot._guild)
        if not config.get("member_logs"):
            return
        log_channel = self.bot.get_channel(config.get("member_logs"))
        hook = await self.get_webhook(log_channel, "User Logs")
        if before.avatar != after.avatar:
            if not after.avatar:
                msg = {
                    "title": "User Avatar Removed | Log",
                    "description": f"**User:** {after}",
                    "thumbnail": after.default_avatar.url,
                }
            else:
                msg = {
                    "title": "User Avatar Updated | Log",
                    "description": f"**User:** {after}",
                    "thumbnail": self.bot.try_asset(
                        after.avatar.url, after.default_avatar.url
                    ),
                }
        elif before.name != after.name:
            msg = {
                "title": "User Name Updated | Log",
                "description": f"**Before:** __{before.name}__#{before.discriminator}\n**After:** __{after.name}__#{after.discriminator}",
            }
        elif before.discriminator != after.discriminator:
            msg = {
                "title": "User Discriminator Updated | Log",
                "description": f"**Before:** {before.name}#__{before.discriminator}__\n**After:** {after.name}#__{after.discriminator}__",
            }
        if msg:
            embed = embed_builder(
                title=msg.get("title"),
                description=msg.get("description"),
                thumbnail=msg.get("thumbnail"),
            )
            await hook.send(embed=embed)

    @commands.Cog.listener(name="on_member_ban")
    async def logs_member_ban(self, guild: discord.Guild, user: discord.User):
        config = await self.db.get_config(guild_id=guild.id)
        if not config.get("moderation_logs"):
            return
        log_channel = self.bot.get_channel(config.get("moderation_logs"))
        hook = await self.get_webhook(log_channel, "Moderation Logs")
        async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if log.user.id == self.bot.user.id:
                return
            user = f"**Banned By:** {log.user}\n"
            reason = (
                f"**Reason:** ```\n{'Unspecified' if not log.reason else log.reason}```"
            )
        name = f"**Member:** {user}\n"
        mention = f"**Mention:** {user.mention}\n"
        msg = {
            "title": "Member Banned | Log",
            "description": f"{name}{mention}{user}{reason}",
        }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_member_unban")
    async def logs_member_unban(self, guild: discord.Guild, user: discord.User):
        config = await self.db.get_config(guild_id=guild.id)
        if not config.get("moderation_logs"):
            return
        log_channel = self.bot.get_channel(config.get("moderation_logs"))
        hook = await self.get_webhook(log_channel, "Moderation Logs")
        async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
            if log.user.id == self.bot.user.id:
                return
            user = f"**Unbanned By:** {log.user}\n"
            reason = (
                f"**Reason:** ```\n{'Unspecified' if not log.reason else log.reason}```"
            )
        name = f"**Member:** {user}\n"
        msg = {"title": "Member Unbanned | Log", "description": f"{name}{user}{reason}"}
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_message_edit")
    async def logs_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return
        config = await self.db.get_config(guild_id=before.guild.id)
        if not config.get("message_logs"):
            return
        log_channel = self.bot.get_channel(config.get("message_logs"))
        hook = await self.get_webhook(log_channel, "Message Logs")
        name = f"**Message Author:** {before.author}\n"
        beforemsg = f"**Before**: ```\n{before.content}```\n"
        beforetime = f"**Message Sent:** {discord.utils.format_dt(before.created_at, style='R')}\n"
        aftermsg = f"**After:** ```\n{after.content}```\n"
        msglink = after.jump_url
        msg = {
            "title": "Messaged Edited | Log",
            "description": f"{name}{beforetime}{beforemsg}{aftermsg}",
        }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description"), url=msglink
        )
        await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_message_delete")
    async def logs_message_delete(self, msg: discord.Message):
        config = await self.db.get_config(guild_id=msg.guild.id)
        if not config.get("message_logs"):
            return
        time = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
        logs = [
            log
            async for log in msg.guild.audit_logs(
                limit=1, action=discord.AuditLogAction.message_delete, after=time
            )
        ]
        if len(logs):
            deleted_by = f"**Deleted By:** {logs[0].user}\n"
        else:
            deleted_by = ""
        log_channel = self.bot.get_channel(config.get("message_logs"))
        hook = await self.get_webhook(log_channel, "Message Logs")
        name = f"**Message Author:** {msg.author}\n"
        content = f"**Content**: ```\n{msg.content}```"
        channel = f"**Channel:** {msg.channel.mention}\n"
        time_sent = (
            f"**Message Sent:** {discord.utils.format_dt(msg.created_at, style='R')}\n"
        )
        msg = {
            "title": "Messaged Deleted | Log",
            "description": f"{name}{deleted_by}{channel}{time_sent}{content}",
        }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_guild_role_delete")
    async def logs_guild_role_delete(self, role: discord.Role):
        config = await self.db.get_config(guild_id=role.guild.id)
        if not config.get("guild_logs"):
            return
        log_channel = self.bot.get_channel(config.get("guild_logs"))
        hook = await self.get_webhook(log_channel, "Server Logs")
        async for log in role.guild.audit_logs(
            action=discord.AuditLogAction.role_delete, limit=1
        ):
            user = f"**Deleted By:** {log.user}\n"
        name = f"**Name:** {role.name}\n"
        msg = {"title": "Role Deleted | Log", "description": f"{name}{user}"}
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_guild_role_create")
    async def logs_guild_role_create(self, role: discord.Role):
        config = await self.db.get_config(guild_id=role.guild.id)
        if not config.get("guild_logs"):
            return
        log_channel = self.bot.get_channel(config.get("guild_logs"))
        hook = await self.get_webhook(log_channel, "Server Logs")
        async for log in role.guild.audit_logs(
            action=discord.AuditLogAction.role_create, limit=1
        ):
            user = f"**Created By:** {log.user}\n"
        name = f"**Name:** {role.name}\n"
        mention = f"**Mention:** {role.mention}"
        colour = f"**Colour:** {role.colour}"
        msg = {
            "title": "Role Deleted | Log",
            "description": f"{name}{mention}{colour}{user}",
        }
        embed = embed_builder(
            title=msg.get("title"),
            description=msg.get("description"),
            thumbnail=self.bot.try_asset(role.icon),
        )
        await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_guild_role_update")
    async def logs_guild_role_update(self, before: discord.Role, after: discord.Role):
        config = await self.db.get_config(guild_id=before.guild.id)
        if not config.get("guild_logs"):
            return
        log_channel = self.bot.get_channel(config.get("guild_logs"))
        hook = await self.get_webhook(log_channel, "Server Logs")
        async for log in before.guild.audit_logs(
            action=discord.AuditLogAction.role_update, limit=1
        ):
            user = f"**Updated By:** {log.user}\n"
        msg = None
        if before.colour != after.colour:
            changed = f"**Before:** {before.colour}\n**After:** {after.colour}"
            msg = {
                "title": "Role Name Updated | Log",
                "description": f"{changed}{user}",
            }
        elif before.hoist != after.hoist:
            changed = (
                f"**Before:** {'Hoisted' if before.hoist else 'Not Hoisted'}\n"
                f"**After:** {'Hoisted' if after.hoist else 'Not Hoisted'}"
            )
            msg = {
                "title": "Role Hoist Updated | Log",
                "description": f"{changed}{user}",
            }
        elif before.icon != after.icon:
            msg = {
                "title": f"Role Icon {'Removed' if not after.icon else 'Updated'} | Log",
                "description": f"{user}",
                "thumbnail": f"{self.bot.try_asset(after.icon)}",
            }
        elif before.mentionable != after.mentionable:
            changed = (
                f"**Before:** {'Mentionable' if before.hoist else 'Not Mentionable'}\n"
                f"**After:** {'Mentionable' if after.hoist else 'Not Mentionable'}"
            )
            msg = {
                "title": "Role Mentionable State Updated | Log",
                "description": f"{changed}{user}",
            }
        elif before.name != after.name:
            changed = f"**Before:** {before.name}\n**After:** {after.name}"
            msg = {
                "title": "Role Name Updated | Log",
                "description": f"{changed}{user}",
            }
        elif before.permissions != after.permissions:
            b_enabled = [
                str(name).replace("guild", "server").replace("_", " ").title()
                for name, value in set(before.permissions)
                if value is True
            ]
            b_disabled = [
                str(name).replace("guild", "server").replace("_", " ").title()
                for name, value in set(before.permissions)
                if value is False
            ]
            a_enabled = [
                str(name).replace("guild", "server").replace("_", " ").title()
                for name, value in set(after.permissions)
                if value is True
            ]
            a_disabled = [
                str(name).replace("guild", "server").replace("_", " ").title()
                for name, value in set(after.permissions)
                if value is False
            ]
            added = ""
            if b_enabled != a_enabled:
                added = set(a_enabled) - set(b_enabled)
                if added:
                    added = f"**Added:** {', '.join(added)}"
                else:
                    added = ""
            removed = ""
            if a_disabled != b_disabled:
                removed = set(a_disabled) - set(b_disabled)
                if removed:
                    removed = f"**Removed:** {', '.join(removed)}"
                else:
                    removed = ""
            msg = {
                "title": "Role Permissions Updated | Log",
                "description": added + removed,
            }
        if msg:
            embed = embed_builder(
                title=msg.get("title"),
                description=msg.get("description"),
                thumbnail=msg.get("thumbnail"),
            )
            await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)

    @commands.Cog.listener(name="on_voice_state_update")
    async def logs_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        config = await self.db.get_config(guild_id=before.guild.id)
        if not config.get("voice_logs"):
            return
        log_channel = self.bot.get_channel(config.get("voice_logs"))
        hook = await self.get_webhook(log_channel, "Voice Logs")
        if before.channel and after.channel and before.channel != after.channel:
            time = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
            logs = [
                log
                async for log in member.guild.audit_logs(
                    limit=1, action=discord.AuditLogAction.member_move, after=time
                )
            ]
            if len(logs):
                user = f"\n**Moved By:** {logs[0].user}"
            else:
                user = ""
            msg = {
                "title": "Member Moved Voice Channel",
                "description": f"**Member:** {member}\n**Old Channel:** {before.channel.mention}\n"
                f"**New Channel:** {after.channel.mention}{user}",
            }
        elif not before.channel and after.channel:
            msg = {
                "title": "Member Joined Voice Channel",
                "description": f"**Member:** {member}\n**Channel:** {after.channel.mention}",
            }
        elif before.channel and not after.channel:
            msg = {
                "title": "Member Left Voice Channel",
                "description": f"**Member:** {member}\n**Channel:** {before.channel.mention}",
            }
        elif before.deaf != after.deaf:
            if after.deaf:
                time = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
                logs = [
                    log
                    async for log in member.guild.audit_logs(
                        limit=1, action=discord.AuditLogAction.member_update
                    )
                    if log.target.id == member.id
                ]
                user = "" if not len(logs) else f"**Deafened By:** {logs[0].user}"
                msg = {
                    "title": "Member Voice Deafened",
                    "description": f"**Member:** {member}{user}",
                }
            elif before.deaf:
                time = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
                logs = [
                    log
                    async for log in member.guild.audit_logs(
                        limit=1, action=discord.AuditLogAction.member_update
                    )
                    if log.target.id == member.id
                ]
                user = "" if not len(logs) else f"**Undeafened By:** {logs[0].user}"
                msg = {
                    "title": "Member Voice Undeafened",
                    "description": f"**Member:** {member}{user}",
                }
        elif before.mute != after.mute:
            if after.mute:
                time = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
                logs = [
                    log
                    async for log in member.guild.audit_logs(
                        limit=1, action=discord.AuditLogAction.member_update
                    )
                    if log.target.id == member.id
                ]
                user = "" if not len(logs) else f"**Muted By:** {logs[0].user}"
                msg = {
                    "title": "Member Voice Muted",
                    "description": f"**Member:** {member}{user}",
                }
            elif before.deaf:
                time = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
                logs = [
                    log
                    async for log in member.guild.audit_logs(
                        limit=1, action=discord.AuditLogAction.member_update
                    )
                    if log.target.id == member.id
                ]
                user = "" if not len(logs) else f"**Unmuted By:** {logs[0].user}"
                msg = {
                    "title": "Member Voice Unmuted",
                    "description": f"**Member:** {member}{user}",
                }
        if msg:
            embed = embed_builder(
                title=msg.get("title"), description=msg.get("description")
            )
            await hook.send(embed=embed, avatar_url=self.bot.user.display_avatar.url)
