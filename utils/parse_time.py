import discord
from discord.ext import commands

# Discord Imports

import re
from dateutil.relativedelta import relativedelta
import parsedatetime as pdt
import datetime

# Regular Imports

from bot import ExultBot


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