from discord import Embed
#Discord Imports

from typing import Union
#Regular Imports

from .ic.bot import ExultBot
from .types.hextype import HexType
#Local Imports

def embed_builder(*, title:Union[str, None]=None, description:Union[str, None]=None, colour:HexType=ExultBot.red, 
                  timestamp:Union[bool, None]=None, author:Union[list, str, None]=None, footer:Union[list, str, None]=None,
                  thumbnail:Union[str, None]=None, image:Union[str, None]=None, fields:Union[list, None]=None, url:str=None):
    embed = Embed()
    if title: embed.title = title
    if description: embed.description = description
    if timestamp: embed.timestamp = timestamp
    embed.colour = colour
    if thumbnail: embed.set_thumbnail(url=thumbnail)
    if image: embed.set_image(url=image)
    if url: embed.url = url
    if author:
        if isinstance(author, list):
            embed.set_author(icon_url=author[0], name=author[1])
        elif isinstance(author, str):
            embed.set_author(name=author)
    if footer:
        if isinstance(footer, list):
            embed.set_footer(icon_url=footer[0], name=footer[1])
        elif isinstance(footer, str):
            embed.set_footer(text=footer)
    if fields:
        for field in fields:
            try:
                embed.add_field(name=field[0], value=field[1], inline=field[2])
            except IndexError:
                embed.add_field(name=field[0], value=field[1])
    return embed