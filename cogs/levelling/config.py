import discord
from discord import app_commands
from discord.ext import commands

from bot import ExultBot
from utils import *


class LevellingConfig(commands.GroupCog, group_name="levelling"):
    """Levelling Config Commands"""

    def __init__(self, bot: ExultBot):
        self.bot = bot

    announce_channel = app_commands.Group(
        name="announce_channel",
        description="Configure where level-up announcements are made!",
    )
    blacklisted_roles = app_commands.Group(
        name="blacklisted_roles",
        description="Configure the blacklisted roles for levelling!",
    )
    blacklisted_channels = app_commands.Group(
        name="blacklisted_channels",
        description="Configure the blacklisted channels for levelling!",
    )
    custom_message = app_commands.Group(
        name="custom_message",
        description="Configure the level-up announcement message!",
    )
    custom_rewards = app_commands.Group(
        name="custom_rewards", description="Configure custom rewards for levelling!"
    )

    @announce_channel.command(
        name="set", description="Set what the level-up announcement channel should be."
    )
    async def levelling_announce_channel_set_slash(
        self, itr: discord.Interaction, channel: discord.TextChannel
    ):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        channel_id = channel.id

        await LevellingDB(bot).set_custom_channel(itr.guild.id, channel_id)

        embed = embed_builder(
            title="Success!",
            description=f"Level-up announcements will now be sent to {channel.mention}!",
        )
        await followup.send(embed=embed)

    @announce_channel.command(
        name="disable", description="Disable the level-up announcement channel."
    )
    async def levelling_announce_channel_disable_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        await LevellingDB(bot).remove_custom_channel(itr.guild.id)

        embed = embed_builder(
            title="Success!",
            description=f"Level-up announcements will now be sent in the channel the user levels up in.",
        )
        await followup.send(embed=embed)

    @blacklisted_roles.command(
        name="add", description="Add a role to the levelling role blacklist."
    )
    async def levelling_blacklist_role_add_slash(
        self, itr: discord.Interaction, role: discord.Role
    ):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        role_id = role.id

        if await LevellingDB(bot).add_blacklisted_role(itr.guild.id, role_id):
            embed = embed_builder(
                title="Success!",
                description=f"{role.mention} is now a blacklisted levelling role.",
            )
        else:
            embed = embed_builder(
                title="Failure!", description=f"{role.mention} is already blacklisted!"
            )
        await followup.send(embed=embed)

    @blacklisted_roles.command(
        name="remove", description="Remove a role from the levelling role blacklist."
    )
    async def levelling_blacklist_role_remove_slash(
        self, itr: discord.Interaction, role: discord.Role
    ):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        role_id = role.id

        if await LevellingDB(bot).remove_blacklisted_role(itr.guild.id, role_id):
            embed = embed_builder(
                title="Success!",
                description=f"{role.mention} is no longer a blacklisted levelling role.",
            )
        else:
            embed = embed_builder(
                title="Failure!", description=f"{role.mention} isn't blacklisted!"
            )
        await followup.send(embed=embed)

    @blacklisted_roles.command(
        name="view", description="View the current levelling role blacklist"
    )
    async def levelling_blacklist_role_view_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        blacklist = await LevellingDB(bot).get_blacklisted(itr.guild.id, get="roles")
        if not blacklist:
            embed = embed_builder(
                title="Oops!", description="The levelling role blacklist is empty!"
            )
        else:
            embed = embed_builder(
                title="Levelling Role Blacklist",
                description="\n".join(
                    [itr.guild.get_role(role).mention for role in blacklist]
                ),
            )
        await followup.send(embed=embed)

    @blacklisted_channels.command(
        name="add", description="Add a channel to the levelling channel blacklist."
    )
    async def levelling_blacklist_channel_add_slash(
        self, itr: discord.Interaction, channel: discord.TextChannel
    ):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        channel_id = channel.id

        if await LevellingDB(bot).add_blacklisted_channel(
            itr.guild.id, channel_id=channel_id
        ):
            embed = embed_builder(
                title="Success!",
                description=f"{channel.mention} is now a blacklisted levelling channel.",
            )
        else:
            embed = embed_builder(
                title="Failure!",
                description=f"{channel.mention} is already blacklisted!",
            )
        await followup.send(embed=embed)

    @blacklisted_channels.command(
        name="remove",
        description="Remove a channel from the levelling channel blacklist.",
    )
    async def levelling_blacklist_channel_remove_slash(
        self, itr: discord.Interaction, channel: discord.TextChannel
    ):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        channel_id = channel.id

        if await LevellingDB(bot).remove_blacklisted_channel(
            itr.guild.id, channel_id=channel_id
        ):
            embed = embed_builder(
                title="Success!",
                description=f"{channel.mention} is no longer a blacklisted levelling channel.",
            )
        else:
            embed = embed_builder(
                title="Failure!", description=f"{channel.mention} isn't blacklisted!"
            )
        await followup.send(embed=embed)

    @blacklisted_channels.command(
        name="view", description="View the current levelling channel blacklist"
    )
    async def levelling_blacklist_channel_view_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        blacklist = await LevellingDB(bot).get_blacklisted(itr.guild.id, get="channels")
        if not blacklist:
            embed = embed_builder(
                title="Oops!", description="The levelling channel blacklist is empty!"
            )
        else:
            embed = embed_builder(
                title="Levelling Channel Blacklist",
                description="\n".join(
                    [itr.guild.get_channel(channel).mention for channel in blacklist]
                ),
            )
        await followup.send(embed=embed)

    @custom_message.command(
        name="set", description="Set a custom message for when a user levels up!"
    )
    async def levelling_custom_message_set_slash(
        self, itr: discord.Interaction, message: str
    ):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        if "{user}" not in message and "{level}" not in message:
            embed = embed_builder(
                title="Oops!",
                description="Make sure to include `{user}` and `{level}` in the message!",
            )
            return await followup.send(embed=embed)
        embed = embed_builder(
            title="Success!",
            description=f"`{message}` will now be sent when a user levels up!",
        )
        await followup.send(embed=embed)

    @custom_message.command(
        name="remove",
        description="Removes the current custom message for when a user levels up.",
    )
    async def levelling_custom_message_remove_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        await LevellingDB(bot).remove_custom_message(itr.guild.id)

        embed = embed_builder(
            title="Success!",
            description="The default announce message will now be used for when a user levels up.",
        )
        await followup.send(embed=embed)

    @custom_rewards.command(
        name="add", description="Add a custom reward for reaching a certain level!"
    )
    async def levelling_custom_reward_add_slash(
        self, itr: discord.Interaction, level: int, role: discord.Role
    ):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        role_id = role.id

        added = await LevellingDB(bot).add_reward(itr.guild.id, level, role_id)
        if not added:
            embed = embed_builder(
                title="Oops!", description="That role is already a level role reward!"
            )
        else:
            embed = embed_builder(
                title="Success!",
                description=f"Users will now receive {role.mention} when they reach level `{level}`!",
            )
        await followup.send(embed=embed)

    @custom_rewards.command(
        name="remove",
        description="Remove a custom reward for reaching a certain level.",
    )
    async def levelling_custom_reward_remove_slash(
        self, itr: discord.Interaction, level: int, role: discord.Role
    ):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        role_id = role.id

        added = await LevellingDB(bot).remove_reward(
            itr.guild.id, level, role_id=role_id
        )
        if not added:
            embed = embed_builder(
                title="Oops!", description="That role isn't a level role reward!"
            )
        else:
            embed = embed_builder(
                title="Success!",
                description=f"Users will no longer receive {role.mention} when they reach level `{level}`!",
            )
        await followup.send(embed=embed)

    @custom_rewards.command(name="view", description="View all levelling rewards.")
    async def levelling_custom_reward_view_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        _rewards = await LevellingDB(bot).get_rewards(itr.guild.id)
        sorted_keys = sorted(_rewards)
        rewards = ""
        for key in sorted_keys:
            rewards += f"**Level {key}:** {itr.guild.get_role(_rewards[key]).mention}\n"

        embed = embed_builder(title="Levelling Role Rewards", description=rewards)
        await followup.send(embed=embed)
