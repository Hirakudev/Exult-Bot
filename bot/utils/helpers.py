from discord import Embed, Interaction
from discord.ext.commands import BadArgument, Context
#Discord Imports

from typing import Union
import re
from dateutil.relativedelta import relativedelta
import parsedatetime as pdt
import datetime
import pytz
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

class ShortTime:
    compiled = re.compile("""(?:(?P<years>[0-9])(?:years?|y))?             # e.g. 2y
                             (?:(?P<months>[0-9]{1,2})(?:months?|mo))?     # e.g. 2months
                             (?:(?P<weeks>[0-9]{1,4})(?:weeks?|w))?        # e.g. 10w
                             (?:(?P<days>[0-9]{1,5})(?:days?|d))?          # e.g. 14d
                             (?:(?P<hours>[0-9]{1,5})(?:hours?|h))?        # e.g. 12h
                             (?:(?P<minutes>[0-9]{1,5})(?:minutes?|m))?    # e.g. 10m
                             (?:(?P<seconds>[0-9]{1,5})(?:seconds?|s))?    # e.g. 15s
                          """, re.VERBOSE)

    def __init__(self, argument, *, now=None):
        match = self.compiled.fullmatch(argument)
        if match is None or not match.group(0):
            raise BadArgument('invalid time provided')

        data = { k: int(v) for k, v in match.groupdict(default=0).items() }
        now = now or datetime.datetime.now(datetime.timezone.utc)
        self.dt = now + relativedelta(**data)

    @classmethod
    async def convert(cls, ctx, argument):
        return cls(argument, now=ctx.message.created_at)

class HumanTime:
    calendar = pdt.Calendar(version=pdt.VERSION_CONTEXT_STYLE)

    def __init__(self, argument, *, now=None):
        now = now or datetime.datetime.utcnow()
        dt, status = self.calendar.parseDT(argument, sourceTime=now)
        if not status.hasDateOrTime:
            raise BadArgument("Make sure you format your duration correctly! `(e.g. 5 hours 30 minutes)`")
        
        if not status.hasTime:
            dt = dt.replace(hour=now.hour, minute=now.minute, second=now.second, microsecond=now.microsecond)

        self.dt = dt
        self._past = dt < now

    @classmethod
    async def convert(cls, ctx, argument):
        if isinstance(ctx, Interaction):
            return cls(argument, now=ctx.created_at)
        elif isinstance(ctx, Context):
            return cls(argument, now=ctx.message.created_at)

class Time(HumanTime):
    def __init__(self, argument, *, now=None):
        try:
            o = ShortTime(argument, now=now)
        except Exception as e:
            super().__init__(argument)
        else:
            self.dt = o.dt
            self._past = False

class FutureTime(Time):
    def __init__(self, argument, *, now=None):
        argument_list = list(argument)
        if " " not in argument_list:
            pos = -1
            for c in argument_list:
                pos += 1
                if str(c).isalpha():
                    break
            argument_list.insert(pos, " ")
            argument = "".join([z for z in argument_list])
        super().__init__(argument, now=now)

        if self._past:
            raise BadArgument("This time is in the past.")

def time_handler(time) -> datetime.datetime:
    time = FutureTime(time).dt
    try:
        localised = ExultBot.time(time)
    except:
        raise BadArgument("Make sure you format your duration correctly! `(e.g. 5 hours 30 minutes)`")
    return localised