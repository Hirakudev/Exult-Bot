from discord import Embed
from discord.utils import utcnow
from typing import Union
import re
import datetime

class hextype:
    def __init__(self, x):
        if isinstance(x, str):
            self.val = int(x, 16)
        elif isinstance(x, int):
            self.val = int(str(x), 16)
    def __str__(self):
        return hex(self.val)

def embed_builder(*, title:Union[str, None]=None, description:Union[str, None]=None, colour:hextype=0xfb5f5f, 
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

class Time:
    def handler(time):
        secsearch = re.search("s?ec|s", time)
        minsearch = re.search("m?in|m", time)
        hoursearch = re.search("h?our|h", time)
        daysearch = re.search("d?ay|d", time)
        nums = re.findall("\d", time)
        num = "".join(nums)

        if secsearch:
            dtype = "seconds"
        if minsearch:
            dtype = "minutes"
        if hoursearch:
            dtype = "hours"
        if daysearch:
            dtype = "days"
        if int(num) == 1:
            dtype = dtype[:-1]
        return [num, dtype]

    def parsedate(date=utcnow()):
        timestamp = datetime.datetime.timestamp(date)
        timestamp = str(timestamp).split('.', 1)[0]
        return f"<t:{timestamp}:R>"

    def formatdate(date=utcnow()):
        return date.strftime("%d/%m/%Y %H:%M")

    def convert_for_command(time: Union[datetime.datetime, list]):
        if isinstance(time, list):
            num = int(time[0])
            ttype = str(time[1])
            if ttype.startswith("s"):  
                return datetime.datetime.utcnow() + datetime.timedelta(seconds=num)
            elif ttype.startswith("mi"):
                return datetime.datetime.utcnow() + datetime.timedelta(minutes=num)
            elif ttype.startswith("h"):
                return datetime.datetime.utcnow() + datetime.timedelta(hours=num)
            elif ttype.startswith("d"):
                return datetime.datetime.utcnow() + datetime.timedelta(days=num)
        elif isinstance(time, datetime.datetime):
            return datetime.datetime.utcnow() + time
        
    def minimalise_seconds(seconds):
        if seconds < 60:
            return f"{seconds} seconds"
        m, s = divmod(seconds, 60)
        if m < 60:
            return f"{m} minutes and {s} seconds"
        h, m = divmod(m, 60)
        if h < 24:
            return f"{h} hours, {m} minutes"
        d, h = divmod(h, 24)
        if d < 7:
            return f"{d} days, {h} hours"
        w, d = divmod(d, 7)
        return f"{w} weeks, {d} days"
        
def get_chunks(interval: int, array: list):
    """split up an array into a two dimensional array with the interval specified"""
    total = []
    a = 0
    if len(array) <= interval:
        return [array]
    for i in range(len(array) // interval):
        chunks = []
        for _ in range(interval):
            chunks.append(array[a])
            a += 1
        total.append(chunks)
    if len(array) % interval != 0:
        total.append(array[a:])
    return total