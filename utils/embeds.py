
from traceback import StackSummary, extract_tb, print_tb
import discord

# Discord Imports

from typing import Union


# Regular Imports

from bot import ExultBot
from .helpers import HexType
from .views.error import ErrorButtons

# Local Imports


def embed_builder(
    *,
    title: str = None,
    description: str = None,
    colour: HexType = ExultBot.red,
    timestamp: bool = None,
    author: Union[list, str] = None,
    footer: Union[list, str] = None,
    thumbnail: str = None,
    image: str = None,
    fields: list = None,
    url: str = None,
):
    embed = discord.Embed()
    if title:
        embed.title = title
    if description:
        embed.description = description
    if timestamp:
        embed.timestamp = timestamp
    embed.colour = colour
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    if url:
        embed.url = url
    if author:
        if isinstance(author, list):
            embed.set_author(icon_url=author[0], name=author[1])
        elif isinstance(author, str):
            embed.set_author(name=author)
    if footer:
        if isinstance(footer, list):
            embed.set_footer(icon_url=footer[0], text=footer[1])
        elif isinstance(footer, str):
            embed.set_footer(text=footer)
    if fields:
        for field in fields:
            try:
                embed.add_field(name=field[0], value=field[1], inline=field[2])
            except IndexError:
                embed.add_field(name=field[0], value=field[1])
    return embed


class ErrorEmbed(discord.Embed):
    def __init__(self, *, client:ExultBot = ..., error:Exception = ..., **kwargs):
        super().__init__()
        self.colour = discord.Colour.red()
        self.set_footer(text="An Error has Occurred")
        self.title = f"{error.__class__.__name__} Error"
        self.timestamp = discord.utils.utcnow()
        self.client = client
        self.error = error

    async def send(self):
        error_log = self.client.get_channel(978641023850909776)
        desc = {"preview": f"```{StackSummary.from_list(extract_tb(self.error.__traceback__)).format()[0]}```",
                "full": f"```{''.join(StackSummary.from_list(extract_tb(self.error.__traceback__)).format())}```"}
        
        ErrorButtons(descs = desc, embed = self, message = await error_log.send(embed = self))
        ...