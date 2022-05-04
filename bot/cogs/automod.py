from discord.ext.commands import Cog, Bot
from discord import Object, app_commands, Interaction, TextChannel, Message
import asyncio
import discord


class Modder:
    def __init__(self, time_range=8, max_messages=5, max_consecutive_count=5):
        self.spam_count = {}
        self.consecutive_count = {}
        self.max_consecutive_count = max_consecutive_count
        self.time_range = time_range
        self.max_messages = max_messages

    async def removeFromSpam(self, author: int):
        await asyncio.sleep(self.time_range)
        if author in self.spam_count:
            del self.spam_count[author]

    async def handle_consecutives(self, msg) -> bool:
        author = msg.author.id
        if author not in self.consecutive_count:
            self.consecutive_count[author] = [msg.content, 1]
        else:
            if msg.content == self.consecutive_count[author][0]:
                self.consecutive_count[author][1] += 1
                if self.consecutive_count[author][1] >= self.max_consecutive_count:
                    del self.consecutive_count[author]
                    await msg.channel.purge(limit=self.max_consecutive_count + 1, check=lambda x: x.author.id == author)
                    await msg.channel.send("Do not send repeated text over and over again it is very rude ಠ_ಠ",
                                           delete_after=5)
                    return True
                return False
            else:
                del self.consecutive_count[author]
        return False

    async def handle_spam(self, msg) -> bool:
        author = msg.author.id
        if author not in self.spam_count:
            self.spam_count[author] = 1
            asyncio.create_task(self.removeFromSpam(author))
        else:
            self.spam_count[author] += 1
            if self.spam_count[author] >= self.max_messages:
                del self.spam_count[author]
                await msg.channel.purge(limit=self.max_messages + 1, check=lambda x: x.author.id == author)
                await msg.author.send("ಠ_ಠ Please do not spam it is very rude")
                return True
        return False

    async def handle_msg(self, msg: Message) -> bool:
        c = msg.content
        words = c.split()
        repeats = 0
        word_repeats = 0
        if len(c) <= 45:
            return False
        for i in range(len(c) - 2):
            if c[i] == c[i + 1]:
                repeats += 1
        if len(words) > 2:
            for i in range(len(words) - 2):
                if words[i] == words[i + 1]:
                    word_repeats += 1
        percent = max(repeats / len(c), word_repeats / len(words)) * 100
        if percent > 60 or len(words) / len(c) < 0.07:
            await msg.delete()
            await msg.channel.send(
                f"<@!{msg.author.id}> Don't send mass repeated text in a message, otherwise I have to waste my time "
                f"deleting your pathetic little messages", delete_after=5)
            return True
        return False

    async def check_all(self, msg):
        if msg.author.bot:
            return
        for process in dir(self):
            if process.startswith('handle_') and await eval('self.' + process + '(msg)'):
                return


async def analyseForBlacklisted(message, blacklisted):
    c = message.content.split()
    for word in c:
        for b in blacklisted:
            if word == b:
                return await message.delete()


class Automod(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.modder = Modder(9, 5, 6)

    @app_commands.command(name='automod', description='automate modding in a channel specified')
    async def automod_slash(self, interaction: Interaction, channel: TextChannel):
        """Add channel ID to a db"""
        pass

    @app_commands.command(name='showautomod', description='show automated modding channels')
    async def showAutomod(self, interaction: Interaction):
        channels = [x for x in await self.get_automod(interaction.guild.id) if self.bot.get_channel(x)]  # get from ur db
        if not channels:
            return await interaction.response.send_message("There are no automod channels :(")
        channels = map(lambda x: f"<#{x}>", channels)
        await interaction.response.send_message(
            embed=discord.Embed(title="Automod Channels", description=', '.join(channels), colour=0x00af0c).set_footer(
                text="To add or remove a channel do this command and mention a channel"
            ))

    @app_commands.command(name='blacklist', description="Add a word/remove it from blacklist, so when someone says it, the message will be deleted")
    async def blacklist(self, interaction: Interaction, word: str):
        """My method of adding a word to a db. Change this so it works for ur db.."""
        blacklisted = await self.get_blacklisted(interaction.guild.id)  # get from ur db instead of this
        message = " has been **added** to the blacklisted words"
        if len(blacklisted) > 25 or len(word) > 50:
            return await interaction.response.send_message(embed=discord.Embed(
                description="```yaml\nThis is an invalid request because of one or more of the causes:\n"
                            "-You have reached the maximum limit of storing blacklisted words (25 words)\n"
                            "-Your word exceeds the maximum amount of characters (10 characters)```", colour=0xff0000))
        if word in blacklisted:
            message = " has been **removed** to the blacklisted words"
            blacklisted.remove(word)
        else:
            blacklisted.append(word)
        await self.db.update_server('blacklist_words', interaction.guild.id, 'blacklisted', blacklisted)
        await interaction.response.send_message(embed=discord.Embed(description=word + message, colour=0x08ff05))

    @app_commands.command(name='showblacklist', description="Show words from blacklist")
    async def showBlacklisted(self, interaction: Interaction):
        words = await self.get_blacklisted(interaction.guild.id)  # change this so it gets words from ur db
        if not words:
            return await interaction.response.send_message("There are no blacklisted words..")
        words = map(lambda x: f"`{x}`", words)
        await interaction.response.send_message(
            embed=discord.Embed(title="Blacklisted words", description=', '.join(words), colour=0x00af0c).set_footer(
                text="To add or remove a word do this command and provide a word/The word to remove if it already in the blacklist"
            ))

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.guild_permissions.manage_messages:
            return

        # if message.channel.id is in the database of channels that have the automod on:
        await self.modder.check_all(message)

        # if message.guild.id in the database for blacklisted:
        await analyseForBlacklisted(message, blacklisted_words)



async def setup(bot: Bot):
    await bot.add_cog(Automod(bot), guilds=[Object(guild) for guild in bot.app_guilds])
