"""
The MIT License (MIT)

Copyright (c) 2015 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

Snippets used from RoboDanny in 
lines 103 - 185 https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/time.py
lines 200-264 https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/formats.py
lines 267-274 https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py
"""


import discord
from discord.ext import commands

# Discord Imports

from typing import Union, Iterable, Any
import re
from dateutil.relativedelta import relativedelta
import parsedatetime as pdt
import datetime

# Regular Imports

from bot import ExultBot

# Local Imports


class HexType:
    def __init__(self, x):
        if isinstance(x, str):
            self.val = int(x, 16)
        elif isinstance(x, int):
            self.val = int(str(x), 16)

    def __str__(self):
        return hex(self.val)


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


class ShortTime:
    compiled = re.compile(
        """(?:(?P<years>[0-9])(?:years?|y))?             # e.g. 2y
                             (?:(?P<months>[0-9]{1,2})(?:months?|mo))?     # e.g. 2months
                             (?:(?P<weeks>[0-9]{1,4})(?:weeks?|w))?        # e.g. 10w
                             (?:(?P<days>[0-9]{1,5})(?:days?|d))?          # e.g. 14d
                             (?:(?P<hours>[0-9]{1,5})(?:hours?|h))?        # e.g. 12h
                             (?:(?P<minutes>[0-9]{1,5})(?:minutes?|m))?    # e.g. 10m
                             (?:(?P<seconds>[0-9]{1,5})(?:seconds?|s))?    # e.g. 15s
                          """,
        re.VERBOSE,
    )

    def __init__(self, argument, *, now=None):
        match = self.compiled.fullmatch(argument)
        if match is None or not match.group(0):
            raise commands.BadArgument("invalid time provided")

        data = {k: int(v) for k, v in match.groupdict(default=0).items()}
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
            raise commands.BadArgument(
                "Make sure you format your duration correctly! `(e.g. 5 hours 30 minutes)`"
            )

        if not status.hasTime:
            dt = dt.replace(
                hour=now.hour,
                minute=now.minute,
                second=now.second,
                microsecond=now.microsecond,
            )

        self.dt = dt
        self._past = dt < now

    @classmethod
    async def convert(cls, ctx, argument):
        if isinstance(ctx, discord.Interaction):
            return cls(argument, now=ctx.created_at)
        elif isinstance(ctx, commands.Context):
            return cls(argument, now=ctx.message.created_at)


class Time(HumanTime):
    def __init__(self, argument, *, now=None):
        try:
            o = ShortTime(argument, now=now)
        except:
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
            raise commands.BadArgument("This time is in the past.")


def time_handler(time) -> datetime.datetime:
    time = FutureTime(time).dt
    try:
        localised = ExultBot.time(time)
    except:
        raise commands.BadArgument(
            "Make sure you format your duration correctly! `(e.g. 5 hours 30 minutes)`"
        )
    return localised


class plural:
    def __init__(self, value: int):
        self.value = value

    def __format__(self, format_spec: str) -> str:
        v = self.value
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"


class TabularData:
    def __init__(self):
        self._widths: list[int] = []
        self._columns: list[str] = []
        self._rows: list[list[str]] = []

    def set_columns(self, columns: list[str]):
        self._columns = columns
        self._widths = [len(c) + 2 for c in columns]

    def add_row(self, row: Iterable[Any]) -> None:
        rows = [str(r) for r in row]
        self._rows.append(rows)
        for index, element in enumerate(rows):
            width = len(element) + 2
            if width > self._widths[index]:
                self._widths[index] = width

    def add_rows(self, rows: Iterable[Iterable[Any]]) -> None:
        for row in rows:
            self.add_row(row)

    def render(self) -> str:
        """Renders a table in rST format.
        Example:
        +-------+-----+
        | Name  | Age |
        +-------+-----+
        | Alice | 24  |
        |  Bob  | 19  |
        +-------+-----+
        """

        sep = "+".join("-" * w for w in self._widths)
        sep = f"+{sep}+"

        to_draw = [sep]

        def get_entry(d):
            elem = "|".join(f"{e:^{self._widths[i]}}" for i, e in enumerate(d))
            return f"|{elem}|"

        to_draw.append(get_entry(self._columns))
        to_draw.append(sep)

        for row in self._rows:
            to_draw.append(get_entry(row))

        to_draw.append(sep)
        return "\n".join(to_draw)


def cleanup_code(content: str) -> str:
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:-1])

    # remove `foo`
    return content.strip("` \n")


def get_perms(permissions: discord.Permissions):
    if permissions.administrator:
        return ["Administrator"]
    elevated = [x[0] for x in discord.Permissions.elevated() if x[1] is True]
    wanted_perms = dict({x for x in permissions if x[1] is True and x[0] in elevated})
    return sorted(
        [p.replace("_", " ").replace("guild", "server").title() for p in wanted_perms]
    )


emojis = {
    "bal": "<:Balance:951943457193214014>  ",
    "brav": "<:Bravery:951943457738477608>  ",
    "bril": "<:Brilliance:951943457214169160>  ",
    "hype": "<:Hypesquad:951943457700720660>  ",
    "early": "<:EarlySupporter:951943457621028864>  ",
    "bugh": "<:BugHunter:951943457511964792>  ",
    "bugh2": "<:BugHunter2:951943457629405264>  ",
    "dpart": "<:DiscordPartner:951943457495207986>  ",
    "dstaff": "<:DiscordStaff:951943457721700402>  ",
    "earlydev": "<:EarlyVerifiedBotDev:951943458174689391>  ",
    "dmod": "<:DiscordCertifiedModerator:951945202963198062>  ",
    "bot": "<:VerifiedBot:951943457788813363>  ",
}
