import discord
from discord import app_commands
#Discord Imports

from collections import Counter
import re
#Regular Imports

from utils import *
#Local Imports

class Purge(ExultCog):

    async def purge_messages(self, itr: discord.Interaction, limit: int, check, *, before=None, after=None):
        if limit > 2000:
            return itr.response.send_message(f"Too many messages to purge provided. ({limit}/2000)")

        await itr.response.defer()

        if before is None:
            history = itr.channel.history(limit=1)
            last_message = await history.__anext__()
            before = last_message
        else:
            before = discord.Object(before)

        if after is not None:
            after = discord.Object(after)

        try:
            deleted = await itr.channel.purge(limit=limit, before=before, after=after, check=check)
        except discord.Forbidden as e:
            return await itr.followup.send("I do not have permissions to delete messages.")
        except discord.HTTPException as e:
            return await itr.followup.send(f"Error: {e} (Try a smaller search.)")

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        title = f'{deleted} message{" was" if deleted == 1 else "s were"} removed.'
        messages = []
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'**{name}**: {count}\n' for name, count in spammers)

        to_send = "".join(messages)

        embed = embed_builder(title=title)

        if len(to_send) > 2000:
            return await itr.followup.send(embed=embed)
        embed.description = to_send
        return await itr.followup.send(embed=embed)

    purge = app_commands.Group(name="purge", description="Purge messages in the current channel.")

    @purge.command(name="embeds", description=f"Removes all messages containing embeds in the given range.")
    @app_commands.describe(messages="Number of messages you want to search through.")
    @guild_staff(manage_messages=True)
    async def purge_embeds_slash(self, itr: discord.Interaction, messages: app_commands.Range[int, 1, 2000]):
        await self.purge_messages(itr, messages, lambda m: len(m.embeds))

    @purge.command(name="files", description=f"Removes all messages containing files in the given range.")
    @app_commands.describe(messages="Number of messages you want to search through.")
    @guild_staff(manage_messages=True)
    async def purge_files_slash(self, itr: discord.Interaction, messages: app_commands.Range[int, 1, 2000]):
        await self.purge_messages(itr, messages, lambda m: len(m.attachments))

    @purge.command(name="messages", description=f"Removes all messages in the given range.")
    @app_commands.describe(messages="Number of messages you want to delete.")
    @guild_staff(manage_messages=True)
    async def purge_messages_slash(self, itr: discord.Interaction, messages: app_commands.Range[int, 1, 2000]):
        await self.purge_messages(itr, messages, lambda m: True)

    @purge.command(name="user", description=f"Removes all messages from a certain user.")
    @app_commands.describe(user="The user that you want to purge messages from.", messages="Number of messages you want to search through.")
    @guild_staff(manage_messages=True)
    async def purge_user_slash(self, itr: discord.Interaction, user: discord.Member, messages: app_commands.Range[int, 1, 2000]):
        await self.purge_messages(itr, messages, lambda m: m.author == user)

    @purge.command(name="containing", description=f"Removes all messages containing a given sequence.")
    @app_commands.describe(sequence="The sequence of characters that a message should have to delete it", 
              messages="Number of messages you want to search through.")
    @guild_staff(manage_messages=True)
    async def purge_containing_slash(self, itr: discord.Interaction, sequence: str, messages: app_commands.Range[int, 1, 2000]):
        if len(sequence) < 3:
            return await itr.response.send_message("The sequence must have more than 3 characters.")
        await self.purge_messages(itr, messages, lambda m: sequence in m.content)

    @purge.command(name="bot", description=f"Removes all messages from bots.")
    @app_commands.describe(messages="Number of messages you want to search through.", prefix="If this prefix is in a message, delete the message.")
    @guild_staff(manage_messages=True)
    async def purge_bot_slash(self, itr: discord.Interaction, messages: app_commands.Range[int, 1, 2000], prefix: str=None):
        await self.purge_messages(itr, messages, lambda m: (m.webhook_id is None and m.author.bot) or (prefix and m.content.startswith(prefix)))

    @purge.command(name="emoji", description=f"Removes all messages containing a custom emoji.")
    @app_commands.describe(messages="Number of messages you want to search through.")
    @guild_staff(manage_messages=True)
    async def purge_emoji_slash(self, itr: discord.Interaction, messages: app_commands.Range[int, 1, 2000]):
        custom_emoji = re.compile(r'<a?:[a-zA-Z0-9\_]+:([0-9]+)>')
        await self.purge_messages(itr, messages, lambda m: custom_emoji.search(m.content))

    @purge.command(name="reactions", description=f"Removes all reactions from all messages that have them.")
    @app_commands.describe(messages="Number of messages you want to search through.")
    @guild_staff(manage_messages=True)
    async def purge_reaction_slash(self, itr: discord.Interaction, messages: app_commands.Range[int, 1, 2000]):
        if messages > 2000:
            return await itr.response.send_message(f"Too many messages to purge ({messages}/2000)")

        await itr.response.defer()
        
        total_reactions = 0
        async for message in itr.channel.history(limit=messages):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        embed = embed_builder(title=f"Successfully removed {total_reactions} reactions.")
        await itr.followup.send(embed=embed)