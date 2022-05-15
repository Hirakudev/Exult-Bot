import discord
from discord import app_commands
from discord.ext import commands

from typing import Union

from bot import ExultBot
from utils import *


class TextChannelTransformer(app_commands.Transformer):
    @classmethod
    async def transform(cls, itr: discord.Interaction, value: str):
        if value.isdigit():
            channel = itr.guild.get_channel(int(value))
            if isinstance(channel, discord.TextChannel):
                return channel
            return "not text"
        return value


class LevellingConfig(commands.Cog):
    """Levelling Config Commands"""

    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db = LevellingDB(bot)

    levelling = app_commands.Group(
        name="levelling", description="Configure the levelling feature!"
    )
    l_set = app_commands.Group(
        name="set",
        description="Give levelling config properties a value!",
        parent=levelling,
    )
    l_blacklist = app_commands.Group(
        name="blacklist",
        description="Configure the levelling blacklist!",
        parent=levelling,
    )
    l_reward = app_commands.Group(
        name="reward-role",
        description="Configure the role rewards for levelling!",
        parent=levelling,
    )

    @l_set.command(
        name="announce-channel",
        description="Set where level-up announcements are sent!",
    )
    async def levelling_set_announce_channel_slash(
        self,
        itr: discord.Interaction,
        item: app_commands.Transform[
            Union[str, discord.TextChannel], TextChannelTransformer
        ],
    ):
        await itr.response.defer()
        followup = itr.followup
        channel_id = None
        config = await self.ldb.get_custom_channel(guild_id=itr.guild.id)

        if isinstance(item, discord.TextChannel):
            channel = item
            channel_id = item.id
            if config == channel_id:
                embed = embed_builder(
                    description=f"Level-up Announcements are already set to {channel.mention}!"
                )
                return await followup.send(embed=embed)
        elif item == "current":
            if not config:
                embed = embed_builder(
                    description=f"Level-up Announcements are already set to the current channel!"
                )
                return await followup.send(embed=embed)
            else:
                await self.ldb.remove_custom_channel(guild_id=itr.guild.id)
                embed = embed_builder(
                    description="Level-up announcements will now be sent in the channel the user levels up in!"
                )
                return await followup.send(embed=embed)
        elif item == "not text":
            embed = embed_builder(
                description=f"The channel provided must be a text channel!"
            )
            return await followup.send(embed=embed)
        else:
            channels = [c for c in itr.guild.text_channels if c.name == item.lower()]
            if len(channels) == 1:
                channel = channels[0]
                channel_id = channel.id
            elif len(channels) > 1:
                embed = embed_builder(
                    description=f"Multiple channels with the name `{item}` exist. "
                    "Please use the dropdown provided in the channel menu or provide the channel's ID."
                )
                return await followup.send(embed=embed)
        if not channel_id:
            embed = embed_builder(
                description="Invalid input given. Please try again using the values provided in the autocomplete menu."
            )
        else:
            await self.ldb.set_custom_channel(
                guild_id=itr.guild.id, channel_id=channel_id
            )
            embed = embed_builder(
                description=f"Level-up Announcements will now be sent to {channel.mention}!"
            )
        return await followup.send(embed=embed)

    @levelling_set_announce_channel_slash.autocomplete("item")
    async def levelling_set_announce_channel_autocomplete(
        self, itr: discord.Interaction, current: str
    ):
        channels = [c for c in itr.guild.text_channels]
        choices = [app_commands.Choice(name="current channel", value="current")] + [
            app_commands.Choice(name=f"#{c.name}", value=str(c.id))
            for c in channels
            if current in f"#{c.name}"
        ]
        return choices

    @l_set.command(
        name="message",
        description="Configure the message sent for the level-up announcement!",
    )
    async def levelling_set_message_slash(self, itr: discord.Interaction, message: str):
        await itr.response.defer()
        followup = itr.followup
        embed = None

        if message == "default":
            await self.ldb.remove_custom_message(guild_id=itr.guild.id)
            embed = embed_builder(
                description=f"Reverted custom level-up message to the default announcement!"
            )

        if any(("{user}" not in message, "{level}" not in message)):
            if not embed:
                embed = embed_builder(
                    description="Make sure you include the user who levelled up (`{user}`) AND the level they levelled up to (`{level}`)!"
                )
            return await followup.send(embed=embed)

        if message == "default":
            await self.ldb.remove_custom_message(guild_id=itr.guild.id)
            embed = embed_builder(
                description=f"Reverted custom level-up message to the default announcement!"
            )
        else:
            await self.ldb.set_custom_message(guild_id=itr.guild.id, message=message)
            embed = embed_builder(
                description=f"Level-up announcement message has been set to: ```\n{message}```"
            )
        await followup.send(embed=embed)

    @levelling_set_message_slash.autocomplete("message")
    async def levelling_set_message_autocomplete(
        self, itr: discord.Interaction, current: str
    ):
        choices = ["default"]
        return [app_commands.Choice(name=c, value=c) for c in choices if current in c]

    @l_blacklist.command(
        name="add", description="Add a Role/Channel to the levelling blacklist!"
    )
    @app_commands.rename(_item="item")
    async def levelling_blacklist_add_slash(self, itr: discord.Interaction, _item: str):
        await itr.response.defer()
        followup = itr.followup
        embed = None
        is_added = None

        item = itr.guild.get_channel(int(_item)) or itr.guild.get_role(int(_item))
        if not item:
            embed = embed_builder(
                description=f"Invalid role/channel given!\n**Hint:** Use the autocomplete displayed in the command menu!"
            )
            return await followup.send(embed=embed)

        if isinstance(item, discord.Role):
            if not embed:
                is_added = await self.ldb.add_blacklisted_role(
                    guild_id=itr.guild.id, role_id=item.id
                )
        elif isinstance(item, discord.TextChannel):
            if not embed:
                is_added = await self.ldb.add_blacklisted_channel(
                    guild_id=itr.guild.id, channel_id=item.id
                )
        else:
            embed = embed_builder(
                description="Please make sure the value provided is either a role or a text channel!"
            )
            return await followup.send(embed=embed)
        if is_added:
            embed = embed_builder(
                description=f"{item.mention} is now blacklisted from levelling!"
            )
        if is_added is False:
            embed = embed_builder(description=f"{item.mention} is already blacklisted!")
        await followup.send(embed=embed)

    @levelling_blacklist_add_slash.autocomplete("_item")
    async def levelling_blacklist_add_autocomplete(
        self, itr: discord.Interaction, current: str
    ):
        roles = [r for r in itr.guild.roles[1:] if not r.managed]
        channels = [c for c in itr.guild.text_channels]
        choices = [
            app_commands.Choice(name=f"#{c.name}", value=str(c.id))
            for c in channels
            if current in f"#{c.name}"
        ] + [
            app_commands.Choice(name=f"@{r.name}", value=str(r.id))
            for r in roles
            if current in f"@{r.name}"
        ]
        return choices

    @l_blacklist.command(
        name="remvove",
        description="Remove a Role/Channel from the levelling blacklist!",
    )
    @app_commands.rename(_item="item")
    async def levelling_blacklist_remove_slash(
        self, itr: discord.Interaction, _item: str
    ):
        await itr.response.defer()
        followup = itr.followup
        embed = None
        is_removed = None

        item = itr.guild.get_channel(int(_item)) or itr.guild.get_role(int(_item))
        if not item:
            embed = embed_builder(
                description=f"Invalid role/channel given!\n**Hint:** Use the autocomplete displayed in the command menu!"
            )
            return await followup.send(embed=embed)

        if isinstance(item, discord.Role):
            if not embed:
                is_removed = await self.ldb.remove_blacklisted_role(
                    guild_id=itr.guild.id, role_id=item.id
                )
        elif isinstance(item, discord.TextChannel):
            if not embed:
                is_removed = await self.ldb.remove_blacklisted_channel(
                    guild_id=itr.guild.id, channel_id=item.id
                )
        else:
            embed = embed_builder(
                description="Please make sure the value provided is either a role or a text channel!"
            )
            return await followup.send(embed=embed)
        if is_removed:
            embed = embed_builder(
                description=f"{item.mention} is no longer blacklisted from levelling!"
            )
        if is_removed is False:
            embed = embed_builder(
                description=f"{item.mention} is not already blacklisted!"
            )
        await followup.send(embed=embed)

    @levelling_blacklist_remove_slash.autocomplete("_item")
    async def levelling_blacklist_add_autocomplete(
        self, itr: discord.Interaction, current: str
    ):
        roles = [r for r in itr.guild.roles[1:] if not r.managed]
        channels = [c for c in itr.guild.text_channels]
        choices = [
            app_commands.Choice(name=f"#{c.name}", value=str(c.id))
            for c in channels
            if current in f"#{c.name}"
        ] + [
            app_commands.Choice(name=f"@{r.name}", value=str(r.id))
            for r in roles
            if current in f"@{r.name}"
        ]
        return choices

    @l_reward.command(name="add", description="Add a levelling role reward!")
    async def levelling_role_reward_add_slash(
        self, itr: discord.Interaction, level: int, role: discord.Role
    ):
        await itr.response.defer()
        followup = itr.followup

        if role.managed:
            embed = embed_builder(
                description=f"You cannot assign a bot role as a role reward!"
            )
            return await followup.send(embed=embed)
        is_added = await self.ldb.add_reward(
            guild_id=itr.guild.id, level=level, role_id=role.id
        )
        if is_added:
            embed = embed_builder(
                description=f"{role.mention} will now be given to members when they reach `LEVEL {level}`!"
            )
        if is_added is False:
            embed = embed_builder(
                description=f"{role.mention} is already a role reward!"
            )
        await followup.send(embed=embed)

    @l_reward.command(name="remove", description="Remove a levelling role reward!")
    async def levelling_role_reward_remove_slash(
        self, itr: discord.Interaction, role: discord.Role
    ):
        await itr.response.defer()
        followup = itr.followup

        is_removed = await self.ldb.remove_reward(
            guild_id=itr.guild.id, role_id=role.id
        )
        if is_removed:
            embed = embed_builder(
                description=f"{role.mention} has been removed as a role reward!"
            )
        if is_removed is False:
            embed = embed_builder(description=f"{role.mention} is not a role reward!")
        await followup.send(embed=embed)
