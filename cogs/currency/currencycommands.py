import discord
from discord import app_commands
from discord.ext import commands

import random

from bot import ExultBot
from utils import *


class CurrencyCommands(commands.Cog):
    """Currency Commands"""

    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db = CurrencyDB(bot)

    items = []
    reward_roles = []

    @app_commands.command(
        name="givebal", description="Admin command for giving a user money!"
    )  # type: ignore
    @app_commands.guild_only()
    async def givebal_slash(
        self, itr: KnownInteraction[ExultBot], member: discord.Member, amount: int
    ):
        await itr.response.defer()
        profile = await self.db.update_wallet(itr.guild.id, member.id, amount)
        embed = embed_builder(
            title="Given balance",
            description=f"{member.mention} has been given `{amount}`!\n"
            f"They now have `{profile.get('wallet')}`!",
        )
        await itr.followup.send(embed=embed)

    @app_commands.command(name="daily", description="Claim your daily currency bonus!")
    @app_commands.checks.cooldown(1, 86400)
    async def daily_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        followup: discord.Webhook = itr.followup

        user = await self.db.update_wallet(itr.guild.id, itr.user.id, 100)

        embed = embed_builder(
            title="Daily Claim",
            description=f"Success! You claimed `100` credits!\n**New Total:** {user.get('wallet')}",
        )
        await followup.send(embed=embed)

    @app_commands.command(
        name="weekly", description="Claim your weekly currency bonus!"
    )
    @app_commands.checks.cooldown(1, 604800)
    async def weekly_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        followup: discord.Webhook = itr.followup

        user = await self.db.update_wallet(itr.guild.id, itr.user.id, 1000)

        embed = embed_builder(
            title="Daily Claim",
            description=f"Success! You claimed `1000` credits!\n**New Total:** {user.get('wallet')}",
        )
        await followup.send(embed=embed)

    @app_commands.command(name="rob", description="Rob someone of their cash!")
    @app_commands.checks.cooldown(1, 30)
    async def rob_slash(self, itr: discord.Interaction, member: discord.Member):
        await itr.response.defer()
        await itr.edit_original_message(content=f"Attempting to rob {member.name}...")
        followup: discord.Webhook = itr.followup

        user_to_rob = await self.db.get_user(itr.guild.id, member.id)
        robber = await self.db.get_user(itr.guild.id, itr.user.id)
        wallet = user_to_rob.get("wallet")
        protected = user_to_rob.get("protected")
        robber_protected = robber.get("protected")

        if not protected:
            if not robber_protected:
                if wallet > 250:
                    robbed = int((wallet * random.randint(1, 5)) / 100)
                    robber = await self.db.update_wallet(
                        itr.guild.id, itr.user.id, robbed
                    )
                    victim = await self.db.update_wallet(
                        itr.guild.id, member.id, -abs(robbed)
                    )
                    epayload = {
                        "title": f"You robbed {member.name}!",
                        "description": f"Amount robbed: {robbed}\n"
                        f"Your new wallet total: {robber.get('wallet')}\n"
                        f"{member.name}'s new wallet total: {victim.get('wallet')}",
                    }
                else:
                    epayload = {
                        "title": "Oops!",
                        "description": f"{member.mention} does not have enough credits to be robbed!",
                    }
            else:
                epayload = {
                    "title": "Oops!",
                    "description": f"You're in passive mode, meaning you cannot rob anyone until you disable it.",
                }
        else:
            epayload = {
                "title": "Oops!",
                "description": f"{member.mention} is in passive mode, and cannot be robbed.",
            }

        embed = embed_builder(
            title=epayload.get("title"), description=epayload.get("description")
        )
        await itr.edit_original_message(content=None, embed=embed)

    @app_commands.command(name="work", description="Work for some money!")
    @app_commands.checks.cooldown(1, 14400)
    async def work_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        followup: discord.Webhook = itr.followup

        pay = random.randint(250, 400)
        msg = f"You've completed your shift and earned `{pay}`!\nCome back in 4 hours for your next shift!"
        await self.db.update_wallet(itr.guild.id, itr.user.id, pay)

        embed = embed_builder(title="Work Complete!", description=msg)
        await followup.send(embed=embed)

    @app_commands.command(name="pay", description="Pay someone money!")
    async def pay_slash(
        self, itr: discord.Interaction, member: discord.Member, amount: str
    ):
        await itr.response.defer()
        followup: discord.Webhook = itr.followup
        amount = int(amount)

        payer = await self.db.get_user(itr.guild.id, itr.user.id)
        if payer.get("wallet") < amount:
            msg = {
                "title": "Oops!",
                "description": "You don't have enough money in your wallet to pay this money!",
            }
        else:
            await self.db.update_wallet(itr.guild, itr.user.id, -abs(amount))
            await self.db.update_wallet(itr.guild.id, member.id, amount)
            msg = {
                "title": "Success!",
                "description": f"You have paid {member.mention} `{amount}`!",
            }
        await followup.send(
            embed=embed_builder(
                title=msg.get("title"), description=msg.get("description")
            )
        )

    @app_commands.command(
        name="gamble",
        description="Gamble some of your money for a chance to earn more!",
    )
    # @app_commands.checks.cooldown(1, 10)
    async def gamble_slash(self, itr: discord.Interaction, money: str):
        await itr.response.defer()
        await itr.edit_original_message(content=f"Deducted {money} from account...")
        amount = int(money)

        user = await self.db.get_user(itr.guild.id, itr.user.id)
        if amount > user.get("wallet"):
            msg = {
                "title": "Oops!",
                "description": "You don't have enough money in your wallet to gamble this money!",
            }
        else:
            await itr.edit_original_message(content="Starting Gamble...")
            num_to_get = random.randint(1, 3)
            if num_to_get in [2, 3]:
                if num_to_get == 2:
                    awarded = int(random.choice((amount / 2, amount / 3)))
                elif num_to_get == 3:
                    awarded = amount
                msg = {
                    "title": "It's a win!",
                    "description": f"Congrats! You won the gamble and won `{awarded}`!",
                }
            else:
                msg = {
                    "title": "Oh no!",
                    "description": f"You lost the gamble and lost {amount} :( \nBetter luck next time!",
                }
                awarded = -abs(amount)
            await self.db.update_wallet(itr.guild.id, itr.user.id, awarded)
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await itr.edit_original_message(content=None, embed=embed)

    @app_commands.command(name="deposit", description="Deposit money into your bank!")
    async def deposit_slash(self, itr: discord.Interaction, money: str):
        await itr.response.defer()
        followup: discord.Webhook = itr.followup
        amount = int(money)

        user = await self.db.get_user(itr.guild.id, itr.user.id)
        if amount > user.get("wallet"):
            msg = {
                "title": "Oops!",
                "description": "You don't have enough money in your wallet to deposit this money!",
            }
        else:
            await self.db.update_bank(itr.guild.id, itr.user.id, amount)
            new_user = await self.db.update_wallet(
                itr.guild.id, itr.user.id, -abs(amount)
            )
            bank = new_user.get("bank")
            msg = {
                "title": "Success!",
                "description": f"Successfully deposited `{amount}` into your bank!\nYou now have {bank} in your bank!",
            }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await followup.send(embed=embed)

    @app_commands.command(name="withdraw", description="Withdraw money from your bank!")
    async def withdraw_slash(self, itr: discord.Interaction, money: str):
        await itr.response.defer()
        followup: discord.Webhook = itr.followup
        amount = int(money)

        user = await self.db.get_user(itr.guild.id, itr.user.id)
        if amount > user.get("bank"):
            msg = {
                "title": "Oops!",
                "description": "You don't have enough money in your bank to withdraw this money!",
            }
        else:
            await self.db.update_bank(itr.guild.id, itr.user.id, -abs(amount))
            new_user = await self.db.update_wallet(itr.guild.id, itr.user.id, amount)
            wallet = new_user.get("wallet")
            msg = {
                "title": "Success!",
                "description": f"Successfully withdrew `{amount}` from your bank!\nYou now have {wallet} in your wallet!",
            }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await followup.send(embed=embed)

    @app_commands.command(name="balance", description="Get your wallet balance!")
    async def balance_slash(
        self, itr: discord.Interaction, member: discord.Member = None
    ):
        await itr.response.defer()
        followup: discord.Webhook = itr.followup
        member = member or itr.user

        user = await self.db.get_user(itr.guild.id, member.id)
        msg = {
            "title": "Wallet Balance",
            "description": f"{f'{member.mention} has' if member != itr.user else 'You have'} `{user.get('wallet')}` "
            f"in {'their' if member != itr.user else 'your'} wallet!",
        }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await followup.send(embed=embed)

    @app_commands.command(name="bank", description="Get your bank balance!")
    async def bank_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        followup: discord.Webhook = itr.followup

        user = await self.db.get_user(itr.guild.id, itr.user.id)
        msg = {
            "title": "Bank Balance",
            "description": f"You have `{user.get('bank')}` in your bank!",
        }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await followup.send(embed=embed)

    @app_commands.command(name="buy", description="Buy an item from the shop!")
    @app_commands.rename(_item="item")
    async def buy_slash(self, itr: KnownInteraction[ExultBot], _item: str):
        await itr.response.defer()
        shop = await self.db.get_shop(itr.guild.id)
        items = [i for i in shop if i.get("name") == _item]
        if items:
            item = items[0]
            price = item.get("price")
            profile = await self.db.get_user(itr.guild.id, itr.user.id)
            if profile.get("wallet") > price:
                role_id = item.get("reward_role")
                role = itr.guild.get_role(role_id)
                if role not in itr.user.roles:
                    await self.db.update_wallet(itr.guild.id, itr.user.id, -price)
                    await itr.user.add_roles(role)
                    msg = {
                        "title": "Success!",
                        "description": f"You have successfully bought `{_item}` for `{price}`!\n"
                        f"You have been given the {role.mention} role!",
                    }
                else:
                    msg = {
                        "title": "Oops!",
                        "description": f"It appears you already have the {role.mention} role!",
                    }
            else:
                msg = {
                    "title": "Oops!",
                    "description": "It appears you don't have enough money in your wallet to purchase this item!",
                }
        else:
            msg = {
                "title": "Oops!",
                "description": f"It appears `{_item}` does not exist in the current shop!",
            }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await itr.edit_original_message(content=None, embed=embed)

    @buy_slash.autocomplete("_item")
    async def buy_autocomplete(self, itr: KnownInteraction[ExultBot], current: str):
        if not self.items:
            shop = await self.db.get_shop(itr.guild.id)
            if not shop:
                return []
            self.items = shop
            for i in self.items:
                role = itr.guild.get_role(i.get("reward_role"))
                self.reward_roles.append(role)
        return [
            app_commands.Choice(
                name=f"{i.get('name')} ~ ${i.get('price')}", value=i.get("name")
            )
            for i in self.items
            if current in i.get("name")
            and itr.guild.get_role(i.get("reward_role")) not in itr.user.roles
        ]
