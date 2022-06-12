import discord
from ..helpers import ServerUtils


class TimeStoneModal(
    discord.ui.Modal, title="Server Stats Milestone and TimeZone info."
):
    milestone = discord.ui.TextInput(label="Milestone")
    timezone = discord.ui.TextInput(label="TimeZone")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        return await interaction.response.defer()


class MileStoneModal(discord.ui.Modal, title="Server Stats Milestone info."):
    milestone = discord.ui.TextInput(label="Milestone")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        return self.milestone.value


class TimeZoneModeal(discord.ui.Modal, title="Server Stats TimeZone info."):
    timezone = discord.ui.TextInput(label="TimeZone")

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"TimeZone: {self.timezone.value}")
        return self.timezone.value


class SelectChannels(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Timezone",
                description="Adds a 'Timezone' channel to your server stats.",
                emoji="\U000023f0",
            ),
            discord.SelectOption(
                label="Channels",
                description="Adds a counter of text and voice channels to your server stats.",
                emoji="\U0001f4dc",
            ),
            discord.SelectOption(
                label="MemberCount",
                description="Adds a counter of members to your server stats.",
                emoji="\U0001fac2",
            ),
            discord.SelectOption(
                label="Milestone",
                description="Adds a counter of members to your server stats.",
                emoji="\U0001f4c8",
            ),
            discord.SelectOption(
                label="Status Counter",
                description="Adds a counter of online and offline members to your server stats.",
                emoji="\U0001fac2",
            ),
        ]
        super().__init__(
            placeholder="Choose your channels",
            min_values=1,
            max_values=len(options),
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        _all = list(self.values)
        if "Milestone" in _all and "Timezone" in _all:
            modal = TimeStoneModal()
            await interaction.response.send_modal(modal)
            await modal.wait()
            await interaction.channel.send(
                f"{modal.milestone.value}, {modal.timezone.value}"
            )
            all_choices = list(self.values)
            category: discord.CategoryChannel = await interaction.guild.create_category(
                name="Server Stats"
            )
            await category.edit(position=0)
            return await ServerUtils(
                category=category,
                timezone=modal.timezone.value,
                milestone=int(modal.milestone.value),
            ).create_channels(interaction, all_choices)

        elif "Milestone" in _all:
            modal = MileStoneModal()
            await interaction.response.send_modal(modal)
            await modal.wait()
            all_choices = list(self.values)
            category: discord.CategoryChannel = await interaction.guild.create_category(
                name="Server Stats"
            )
            await category.edit(position=0)
            await ServerUtils(
                category=category, milestone=int(modal.milestone.value)
            ).create_channels(interaction, all_choices)
        elif "Timezone" in _all:
            modal = TimeZoneModeal()
            await interaction.response.send_modal(modal)
            await modal.wait()
            all_choices = list(self.values)
            category: discord.CategoryChannel = await interaction.guild.create_category(
                name="Server Stats"
            )
            await category.edit(position=0)
            await ServerUtils(
                category=category, timezone=modal.timezone.value
            ).create_channels(interaction, all_choices)
        else:
            all_choices = list(self.values)
            category: discord.CategoryChannel = await interaction.guild.create_category(
                name="Server Stats"
            )
            await category.edit(position=0)
            await ServerUtils(category=category).create_channels(
                interaction, all_choices
            )
            await interaction.response.defer()


class DropDownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(SelectChannels())
