import discord
from discord import ui
from typing import TYPE_CHECKING
from uuid import uuid4

from utils.helpers import embed_builder

if TYPE_CHECKING:
    from ..subclasses import Interaction


def generate_custom_id(task: str, panel_name: str = "untitled"):
    code = uuid4().__str__()
    return f"{task}:{panel_name}:{code[:5]}"


class SetPanelNameModal(ui.Modal):
    def __init__(self, msg: discord.Message, view: "CreatePanelView"):
        self.msg = msg
        self.view = view
        super().__init__(
            title="Edit Panel Name",
            timeout=120,
            custom_id=generate_custom_id("setpanel", "namemodal"),
        )
        self.new_panel_name = self.add_item(
            ui.TextInput(
                label="Enter Panel Name:",
                custom_id=generate_custom_id("newpanelnameinput"),
                placeholder="Enter Panel Name...",
            )
        )

    async def on_submit(self, itr: "Interaction"):
        await itr.response.defer(ephemeral=True)
        msg = self.msg
        self.view.panel_name = self.children[0].value
        self.view.embed["title"] = self.view.panel_name
        embed = msg.embeds[0]
        field = embed.fields[0]
        embed.set_field_at(
            0, name=field.name, value=f"`{self.children[0].value}`", inline=True
        )
        await msg.edit(embed=embed)


class SetPanelName(ui.Button):
    def __init__(self):
        super().__init__(
            label="Set Panel Name",
            custom_id=generate_custom_id("setpanel", "name"),
            emoji="🛠️",
            row=0,
        )

    async def callback(self, itr: "Interaction"):
        # Return a modal which then edits the embed with the new panel name
        await itr.response.send_modal(SetPanelNameModal(itr.message, self.view))


class SetPanelCategoryModal(ui.Modal):
    def __init__(self, msg: discord.Message, view: "CreatePanelView"):
        self.msg = msg
        self.view = view
        super().__init__(
            title="Edit Panel Category",
            timeout=120,
            custom_id=generate_custom_id("editpanel" "categorymodal"),
        )
        self.new_panel_name = self.add_item(
            ui.TextInput(
                label="Enter Panel Category:",
                custom_id=generate_custom_id("editpanel", "categoryinput"),
                placeholder="Enter Panel Category...",
            )
        )

    async def on_submit(self, itr: "Interaction"):
        await itr.response.defer(ephemeral=True)
        category_id = int(self.children[0].value)
        category = itr.guild.get_channel(category_id)
        if not category:
            return await itr.response.send_message(
                f"`{category_id}` is not a Valid Category ID!", ephemeral=True
            )
        if not isinstance(category, discord.CategoryChannel):
            return await itr.response.send_message(
                f"`{category_id}` is not a Valid Category ID!", ephemeral=True
            )
        self.view.category = category.id
        msg = self.msg
        embed = msg.embeds[0]
        field = embed.fields[2]
        embed.set_field_at(2, name=field.name, value=f"`{category}`", inline=True)
        await msg.edit(embed=embed)


class SetPanelCategory(ui.Button):
    def __init__(self):
        super().__init__(
            label="Set Category",
            custom_id=generate_custom_id("editpanel", "category"),
            emoji="🛠️",
            row=0,
        )

    async def callback(self, itr: "Interaction"):
        # Return a modal which then edits the embed with the new category name + id
        await itr.response.send_modal(SetPanelCategoryModal(itr.message, self.view))


class WhatIsEmbed(ui.Button):
    def __init__(self, row: int):
        super().__init__(
            style=discord.ButtonStyle.url,
            label="Embed Guide",
            url="https://i.imgur.com/2nhygdA.png",
            emoji="🆘",
            row=row,
        )


class ConfirmAddPanel(ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.green,
            label="Confirm",
            emoji="✅",
            row=2,
            custom_id=generate_custom_id("confirm", "panel"),
        )

    async def callback(self, itr: "Interaction"):
        name = self.view.panel_name
        if not name:
            await itr.response.send_message(
                "Seems like you haven't specified a name for this panel!",
                ephemeral=True,
            )
        channel = self.view.channel
        if not channel:
            await itr.response.send_message(
                "Seems like you haven't specified a channel for this Panel to be sent to yet!",
                ephemeral=True,
            )
        content = self.view.embed.get("content")
        embed = discord.Embed.from_dict(self.view.embed)
        colour = self.view.embed.get("colour")
        if colour:
            print(colour)
            embed.colour = discord.Colour.from_str(colour)
        msg = await channel.send(content=content, embed=embed)
        itr.client.ticketpanels.append(
            {
                "guild_id": itr.guild.id,
                "panel_name": embed.title,
                "ticket_category": self.view.category,
                "message_content": self.view.embed.get("content"),
                "message_embed": embed.to_dict(),
                "message_id": msg.id,
                "views": None,
            }
        )
        await itr.response.send_message(
            f"Successfully sent the Ticket Panel to {channel.mention}!", ephemeral=True
        )
        embed = itr.message.embeds[0]
        embed.remove_field(len(embed.fields))
        await itr.message.edit(
            content=f"✅ Configuration Complete! ({channel.mention})", embed=embed
        )


class SetMessageContentModal(ui.Modal):
    def __init__(self, existing_content: str, view: "CreatePanelView"):
        self.existing_content = existing_content
        self.view = view
        super().__init__(
            title="Edit Message Content",
            timeout=120,
            custom_id=generate_custom_id("embed", "content"),
        )
        self.msg_content = self.add_item(
            ui.TextInput(
                label="Enter Message Content:",
                style=discord.TextStyle.long,
                custom_id=generate_custom_id("editmessagecontentinput"),
                placeholder="Enter Message Content...",
                default=self.existing_content,
            )
        )

    async def on_submit(self, itr: "Interaction"):
        await itr.response.defer(ephemeral=True)
        msg_content = self.children[0].value
        self.view.embed["content"] = msg_content
        embed = discord.Embed.from_dict(self.view.embed)
        colour = self.view.embed.get("colour")
        if colour:
            embed.colour = discord.Colour.from_str(colour)
        await itr.followup.send(
            content=self.view.embed["content"], embed=embed, ephemeral=True
        )


class SetMessageContent(ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label="Set Message Content",
            custom_id=generate_custom_id("embed", "messagecontent"),
            emoji="💬",
            row=1,
        )

    async def callback(self, itr: "Interaction"):
        await itr.response.send_modal(
            SetMessageContentModal(self.view.embed.get("content"), self.view)
        )


class SetEmbedDescriptionModal(ui.Modal):
    def __init__(self, existing_description: str, view: "CreatePanelView"):
        self.existing_description = existing_description
        self.view = view
        super().__init__(
            title="Edit Embed Description",
            timeout=120,
            custom_id=generate_custom_id("embed", "description"),
        )
        self.msg_content = self.add_item(
            ui.TextInput(
                label="Enter Embed Description:",
                style=discord.TextStyle.long,
                custom_id=generate_custom_id("editembeddescriptioninput"),
                placeholder="Enter Embed Description...",
                default=self.existing_description,
            )
        )

    async def on_submit(self, itr: "Interaction"):
        await itr.response.defer(ephemeral=True)
        description = self.children[0].value
        self.view.embed["description"] = description
        embed = discord.Embed.from_dict(self.view.embed)
        colour = self.view.embed.get("colour")
        if colour:
            embed.colour = discord.Colour.from_str(colour)
        await itr.followup.send(
            content=self.view.embed["content"], embed=embed, ephemeral=True
        )


class SetEmbedDescription(ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label="Set Embed Description",
            custom_id=generate_custom_id("embed", "description"),
            emoji="💬",
            row=1,
        )

    async def callback(self, itr: "Interaction"):
        await itr.response.send_modal(
            SetEmbedDescriptionModal(self.view.embed.get("description"), self.view)
        )


class SetEmbedColourSelect(ui.Select):
    def __init__(self):
        options = [
            ("Red", 0xFF0000),
            ("Orange", 0xFFA500),
            ("Yellow", 0xFFFF00),
            ("Green", 0x008000),
            ("Cyan", 0x00FFFF),
            ("Blue", 0x0000FF),
            ("Magenta", 0xFF00FF),
            ("Purple", 0x800080),
            ("White", 0xFFFFFF),
            ("Black", 0x000000),
            ("Grey", 0x808080),
            ("Silver", 0xC0C0C0),
            ("Pink", 0xFFC0CB),
            ("Maroon", 0x800000),
            ("Brown", 0xA52A2A),
            ("Beige", 0xF5F5DC),
            ("Light Grey", 0xD3D3D3),
            ("Lime", 0x00FF00),
            ("Turquoise", 0x40E0D0),
            ("Teal", 0x008080),
            ("Navy Blue", 0x000080),
            ("Indigo", 0x4B0082),
            ("Violet", 0x8A2BE2),
            ("Crimson Red", 0xDC143C),
            ("Slate Grey", 0x708090),
        ]
        fmt_options = sorted(options, key=lambda o: o[0])
        options = [discord.SelectOption(label=o[0], value=o[1]) for o in fmt_options]
        super().__init__(
            custom_id=generate_custom_id("embed", "colours"),
            placeholder="Select a Colour!",
            min_values=0,
            max_values=1,
            options=options,
        )


class SetEmbedColourModal(ui.Modal):
    def __init__(self, existing_colour: str, view: "CreatePanelView"):
        self.existing_colour = existing_colour
        self.view = view
        super().__init__(
            title="Edit Embed Colour",
            timeout=120,
            custom_id=generate_custom_id("embed", "description"),
        )
        self.colour = self.add_item(SetEmbedColourSelect())
        self.custom_colour = self.add_item(
            ui.TextInput(
                label="Enter Embed Colour HEX:",
                style=discord.TextStyle.short,
                custom_id=generate_custom_id("editembedcolourinput"),
                placeholder="Enter Embed Colour HEX...",
                default=self.existing_colour,
                required=False,
            )
        )

    async def on_submit(self, itr: "Interaction"):
        await itr.response.defer(ephemeral=True)
        try:
            colour = self.children[0].values[0]
        except IndexError:
            colour = self.children[1].value
        if colour:
            try:
                colour = hex(int(colour))
            except ValueError:
                if "0x" in colour or "#" in colour:
                    pass
                else:
                    return await itr.followup.send(
                        "Invalid Colour HEX given.", ephemeral=True
                    )
        self.view.embed["colour"] = colour
        embed = discord.Embed.from_dict(self.view.embed)
        embed.colour = discord.Colour.from_str(colour)
        await itr.followup.send(
            content=self.view.embed["content"], embed=embed, ephemeral=True
        )


class SetEmbedColour(ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label="Set Embed Colour",
            custom_id=generate_custom_id("embed", "colour"),
            emoji="🎨",
            row=1,
        )

    async def callback(self, itr: "Interaction"):
        await itr.response.send_modal(
            SetEmbedColourModal(self.view.embed["colour"], self.view)
        )


class SetEmbedThumbnailModal(ui.Modal):
    def __init__(self, existing_thumbnail: str, view: "CreatePanelView"):
        self.existing_thumbnail = existing_thumbnail
        self.view = view
        super().__init__(
            title="Edit Embed Thumbnail",
            timeout=120,
            custom_id=generate_custom_id("embed", "thumbnail"),
        )
        self.thumbnail = self.add_item(
            ui.TextInput(
                label="Enter Embed Thumbnail Image URL:",
                style=discord.TextStyle.short,
                custom_id=generate_custom_id("editembedthumbnailinput"),
                placeholder="Enter Embed Thumbnail Image URL...",
                default=self.existing_thumbnail,
            )
        )

    async def on_submit(self, itr: "Interaction"):
        await itr.response.defer(ephemeral=True)
        thumbnail = self.children[0].value
        self.view.embed["thumbnail"] = {"url": thumbnail}
        embed = discord.Embed.from_dict(self.view.embed)
        colour = self.view.embed.get("colour")
        if colour:
            embed.colour = discord.Colour.from_str(colour)
        await itr.followup.send(
            content=self.view.embed["content"], embed=embed, ephemeral=True
        )


class SetEmbedThumbnail(ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label="Set Embed Thumbnail",
            custom_id=generate_custom_id("embed", "thumbnail"),
            emoji="🖼️",
            row=1,
        )

    async def callback(self, itr: "Interaction"):
        await itr.response.send_modal(
            SetEmbedThumbnailModal(self.view.embed["thumbnail"], self.view)
        )


class SetEmbedImageModal(ui.Modal):
    def __init__(self, existing_image: str, view: "CreatePanelView"):
        self.existing_image = existing_image
        self.view = view
        super().__init__(
            title="Edit Embed Image",
            timeout=120,
            custom_id=generate_custom_id("embed", "image"),
        )
        self.image = self.add_item(
            ui.TextInput(
                label="Enter Embed Image URL:",
                style=discord.TextStyle.short,
                custom_id=generate_custom_id("editembedimageinput"),
                placeholder="Enter Embed Image URL...",
                default=self.existing_image,
            )
        )

    async def on_submit(self, itr: "Interaction"):
        await itr.response.defer(ephemeral=True)
        image = self.children[0].value
        self.view.embed["image"] = {"url": image}
        embed = discord.Embed.from_dict(self.view.embed)
        colour = self.view.embed.get("colour")
        if colour:
            embed.colour = discord.Colour.from_str(colour)
        await itr.followup.send(
            content=self.view.embed["content"], embed=embed, ephemeral=True
        )


class SetEmbedImage(ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label="Set Embed Image",
            custom_id=generate_custom_id("embed", "image"),
            emoji="📷",
            row=1,
        )

    async def callback(self, itr: "Interaction"):
        await itr.response.send_modal(
            SetEmbedImageModal(self.view.embed["image"], self.view)
        )


class GetHelp(ui.Button):
    def __init__(self, row: int):
        super().__init__(
            label="Need Help?",
            custom_id=generate_custom_id("gethelp", "generic"),
            emoji="🆘",
            row=row,
        )

    async def callback(self, itr: "Interaction"):
        embed = embed_builder(
            title="Help | Ticket Configuration",
            fields=[
                [
                    "Set Panel Name",
                    "The Name of your Ticket Panel is simply there to best describe what your panel is about. You can have multiple buttons per panel which all create tickets under the same categories, but serve a slightly different purpose.",
                    False,
                ],
                [
                    "Set Panel Channel",
                    "This will just decipher where the Panel you are currently configuring will be sent. Once you have sent it you can use the `/ticket panel edit` command to add actual buttons that create tickets to it!",
                    False,
                ],
                [
                    "Set Category",
                    "This will decipher where all tickets under this panel are created. Leaving this blank will just create tickets under the same category that the panel has been sent to.",
                    False,
                ],
                [
                    "Embed Configuration",
                    "Not sure what certain embed properties are what? Check the `🆘 Embed Guide` button to find out!",
                    False,
                ],
                [
                    "Think you're finished?",
                    "Once you have everything you need configured, go ahead and press `✅ Confirm` to send the panel!",
                    False,
                ],
            ],
        )
        await itr.response.send_message(embed=embed, ephemeral=True)


class SetPanelChannelModal(ui.Modal):
    def __init__(self, msg: discord.Message, view: "CreatePanelView"):
        self.msg = msg
        self.view = view
        super().__init__(
            title="Edit Panel Channel",
            timeout=120,
            custom_id=generate_custom_id("editpanel" "channelmodal"),
        )
        self.new_panel_channel = self.add_item(
            ui.TextInput(
                label="Enter Panel Channel:",
                custom_id=generate_custom_id("editpanel", "channelinput"),
                placeholder="Enter Panel Channel...",
            )
        )

    async def on_submit(self, itr: "Interaction"):
        await itr.response.defer(ephemeral=True)
        channel_id = int(self.children[0].value)
        channel = itr.guild.get_channel(channel_id)
        if not channel:
            return await itr.response.send_message(
                f"`{channel_id}` is not a Valid Channel ID!", ephemeral=True
            )
        if not isinstance(channel, discord.TextChannel):
            return await itr.response.send_message(
                f"`{channel_id}` is not a Valid Channel ID!", ephemeral=True
            )
        self.view.channel = channel
        msg = self.msg
        embed = msg.embeds[0]
        field = embed.fields[1]
        embed.set_field_at(1, name=field.name, value=f"{channel.mention}", inline=True)
        await msg.edit(embed=embed)


class SetPanelChannel(ui.Button):
    def __init__(self):
        super().__init__(
            label="Set Channel",
            custom_id=generate_custom_id("editpanel", "channel"),
            emoji="🛠️",
            row=0,
        )

    async def callback(self, itr: "Interaction"):
        # Return a modal which then edits the embed with the new category name + id
        await itr.response.send_modal(SetPanelChannelModal(itr.message, self.view))


class CreatePanelView(ui.View):
    def __init__(self):
        self.embed = {
            "content": None,
            "title": None,
            "description": None,
            "type": "rich",
            "colour": None,
            "thumbnail": None,
            "image": None,
        }
        self.panel_name = None
        self.channel = None
        self.category = None
        super().__init__(timeout=None)
        # First Row
        self.add_item(SetPanelName())
        self.add_item(SetPanelChannel())
        self.add_item(SetPanelCategory())
        # Second Row
        self.add_item(SetMessageContent())
        self.add_item(SetEmbedDescription())
        self.add_item(SetEmbedColour())
        self.add_item(SetEmbedThumbnail())
        self.add_item(SetEmbedImage())
        # Third Row
        self.add_item(GetHelp(2))
        self.add_item(WhatIsEmbed(2))
        self.add_item(ConfirmAddPanel())


class EditPanelNameModal(ui.Modal):
    def __init__(self, panel_name: str):
        self.panel_name = panel_name
        super().__init__(
            title="Change Ticket Panel Name",
            timeout=120,
            custom_id=generate_custom_id("editpanelname", "modal"),
        )
        self.add_item(
            ui.TextInput(
                label="Panel Name",
                custom_id=generate_custom_id("editpanelname", "modalinput"),
                placeholder="Enter Panel Name...",
                default=self.panel_name,
                max_length=80,
            )
        )

    async def on_submit(self, itr: "Interaction"):
        new_name = self.children[0].value
        if new_name == self.panel_name:
            return await itr.response.send_message(
                "Name has not been changed, no changes were made to your panel.",
                ephemeral=True,
            )
        updated_panel = None
        for panel in itr.client.ticketpanels:
            if panel.get("panel_name") == new_name:
                if panel.get("guild_id") == itr.guild.id:
                    return await itr.response.send_message(
                        f"You already have a panel with this name! Please Try again."
                    )


class EditPanelName(ui.Button):
    def __init__(self, panel_name: str):
        self.panel_name = panel_name
        super().__init__(
            label="Edit Panel Name",
            custom_id=generate_custom_id("editpanel", "name"),
            emoji="🛠️",
            row=0,
        )

    async def callback(self, itr: "Interaction"):
        return


class EditPanelCategory(ui.Button):
    def __init__(self, panel_category: str):
        self.panel_category = panel_category
        super().__init__(
            label="Edit Panel Category",
            custom_id=generate_custom_id("editpanel", "category"),
            emoji="🛠️",
            row=0,
        )

    async def callback(self, itr: "Interaction"):
        await itr.response.send_message(self.panel_category)


class EditPanelMessage(ui.Button):
    def __init__(self, panel_msg_content: str, panel_embed: dict):
        self.panel_message = panel_msg_content
        self.panel_embed = panel_embed
        super().__init__(
            label="Edit Panel Message",
            custom_id=generate_custom_id("editpanel", "message"),
            emoji="🛠️",
            row=0,
        )

    async def callback(self, itr: "Interaction"):
        await itr.response.send_message(self.panel_message)


class AddTicketType(ui.Button):
    def __init__(self, panel: dict):
        self.panel = panel
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label="Add Ticket Type",
            custom_id=generate_custom_id("paneladd", "tickettype"),
            emoji="➕",
            row=0,
        )

    async def callback(self, itr: "Interaction"):
        await itr.response.send_message(self.panel)


class DeleteTicketPanel(ui.Button):
    def __init__(self, panel: dict):
        self.panel = panel
        super().__init__(
            style=discord.ButtonStyle.danger,
            label="Delete Panel",
            custom_id=generate_custom_id("deletepanel", self.panel.get("panel_name")),
            emoji="🗑️",
            row=1,
        )

    async def callback(self, itr: "Interaction"):
        await itr.response.send_message("Delete Panel")


class ConfirmEditPanel(ui.Button):
    def __init__(self, panel: dict):
        self.panel = panel
        super().__init__(
            style=discord.ButtonStyle.success,
            label="Confirm Changes",
            custom_id=generate_custom_id(
                "confirmeditpanel", self.panel.get("panel_name")
            ),
            emoji="✅",
            row=1,
        )

    async def callback(self, itr: "Interaction"):
        await itr.response.send_message("Confirm Edit Panel")


class EditPanelView(ui.View):
    def __init__(self, panel: dict):
        self.panel = panel
        self.msg_content = panel.get("message_content")
        self.embed = panel.get("message_embed")
        self.panel_name = panel.get("panel_name")
        self.panel_category = panel.get("ticket_category")
        super().__init__(timeout=None)
        # First Row
        self.add_item(AddTicketType(self.panel))
        self.add_item(EditPanelName(self.panel_name))
        self.add_item(EditPanelCategory(self.panel_category))
        self.add_item(EditPanelMessage(self.msg_content, self.embed))
        # Second Row
        self.add_item(GetHelp(1))
        self.add_item(WhatIsEmbed(1))
        self.add_item(DeleteTicketPanel(self.panel))
        self.add_item(ConfirmEditPanel(self.panel))
