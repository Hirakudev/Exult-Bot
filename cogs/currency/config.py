import discord
from discord import app_commands
from discord.ext import commands

from bot import ExultBot
from utils import *


class CurrencyConfig(commands.Cog):
    """Currency Config Commands"""

    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db = CurrencyDB(bot)

    toggle = app_commands.Group(
        name="toggle", description="Toggle a certain setting for the currency feature!"
    )
    shop = app_commands.Group(name="shop", description="Interact with the shop!")
    arrow = "<:arrow:977761315567333426>"

    @toggle.command(
        name="passive", description="Toggle being able to rob and be robbed!"
    )
    async def toggle_passive_slash(self, itr: KnownInteraction[ExultBot]):
        await itr.response.defer()
        new_value = await self.db.toggle_protected(itr.guild.id, itr.user.id)
        await itr.edit_original_message(
            content=f"You will no longer be able to rob or be robbed!"
            if not new_value
            else f"You have entered the danger zone! You are now able to rob, and prone to robbing!"
        )

    @shop.command(name="view", description="View the shop")
    async def shop_view_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        followup: discord.Webhook = itr.followup

        shop = await self.db.get_shop(itr.guild.id)
        if shop:
            items = []
            for i, item in enumerate(shop):
                role = itr.guild.get_role(item.get("reward_role"))
                items.append(
                    (
                        f"Item {i+1}: {item.get('name')}",
                        f"{self.arrow} ID: {item.get('item_id')}\n"
                        f"💲 __Price:__ {item.get('price')}\n"
                        f"🎁 __Role:__ {role.mention}",
                        True,
                    )
                )
            embed = embed_builder(title="Shop", fields=items)
        else:
            embed = embed_builder(
                title="Shop",
                description=f"❌ No items in stock! Try checking back later.",
            )
        await followup.send(embed=embed)

    @shop.command(name="add", description="Add a Role to the shop!")
    async def shop_add_slash(
        self, itr: KnownInteraction[ExultBot], name: str, price: str, role: discord.Role
    ):
        await itr.response.defer()
        item = await self.db.shop_add(itr.guild.id, name, price, role.id)
        if item:
            msg = {
                "title": "Added to shop!",
                "description": f"__Name__: `{name}`\n"
                f"{self.arrow} __ID:__ `{item.get('item_id')}`\n"
                f"💲 __Price:__ `{item.get('price')}`\n"
                f"🎁 __Role:__ {role.mention}",
            }
        else:
            msg = {
                "title": "Oops!",
                "description": f"It appears either the name or role already exists in the shop!",
            }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await itr.edit_original_message(content=None, embed=embed)

    @shop.command(name="remove", description="Remove an item from the shop!")
    async def shop_remove_slash(self, itr: KnownInteraction[ExultBot], name: str):
        await itr.response.defer()
        item = await self.db.shop_remove(itr.guild.id, name)
        if item:
            role = itr.guild.get_role(item.get("reward_role"))
            msg = {
                "title": "Removed from shop!",
                "description": f"__Name:__ `{name}`\n"
                f"{self.arrow} __ID:__ {item.get('item_id')}\n"
                f"💲 __Price:__ `{item.get('price')}`\n"
                f"🎁 __Role:__ {role.mention}",
            }
        else:
            msg = {
                "title": "Oops!",
                "description": f"It appears this item does not exist in the shop!",
            }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await itr.edit_original_message(content=None, embed=embed)
