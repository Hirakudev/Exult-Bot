from discord import Interaction, ButtonStyle
from discord.ui import Button, View

from ..helpers import embed_builder

class AvatarButton(Button):
    def __init__(self, label, style, custom_id):
        super().__init__(style=style, label=label, custom_id=custom_id)
        
    async def callback(self, interaction: Interaction):
        custom_id = interaction.data["custom_id"]
        member = await interaction.client.fetch_user(int(custom_id[6:]))
        await interaction.message.edit(embed=embed_builder(author=[member.display_avatar.url, f"{member.name}'s Avatar"],
                                                            image=member.display_avatar.url))

class BannerButton(Button):
    def __init__(self, label, style, custom_id):
        super().__init__(style=style, label=label, custom_id=custom_id)
        
    async def callback(self, interaction: Interaction):
        custom_id = interaction.data["custom_id"]
        member = await interaction.client.fetch_user(int(custom_id[6:]))
        await interaction.message.edit(embed=embed_builder(author=[member.display_avatar.url, f"{member.name}'s Banner"],
                                                            image=member.banner.url))
        
class AvatarView(View):
    def __init__(self, member):
        super().__init__()
        self.add_item(AvatarButton("View Avatar", ButtonStyle.secondary, f"avatar{member.id}"))
        self.add_item(BannerButton("View Banner", ButtonStyle.secondary, f"banner{member.id}"))