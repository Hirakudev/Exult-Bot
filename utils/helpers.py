import discord

# Discord Imports

from typing import Union, Iterable, Any, List
import kimochi
import humanize

# Regular Imports

from .image_gen.emotion import Marriage

# Local Imports


class HexType:
    def __init__(self, x):
        if isinstance(x, str):
            self.val = int(x, 16)
        elif isinstance(x, int):
            self.val = int(str(x), 16)

    def __str__(self):
        return hex(self.val)


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
        self._widths: List[int] = []
        self._columns: List[str] = []
        self._rows: List[List[str]] = []

    def set_columns(self, columns: List[str]):
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


def create_command(guild: Union[discord.Guild, int], name: str, response: str):
    guild_id = guild.id if isinstance(guild, discord.Guild) else guild
    cmd = (
        "import discord\n"
        "from discord import app_commands\n"
        f"@bot.tree.command(name='{name}')\n"
        f"@app_commands.guilds({guild_id})\n"
        f"async def cc_create(itr: discord.Interaction):\n"
        f"    await itr.response.send_message('{response}')"
    )
    return cmd


class Emotions:
    def __init__(self, kimochi_client: kimochi.Client):
        self.client = kimochi_client

    def determine_action(self, action: str) -> str:
        if action in ["hug", "slap", "poke", "pat", "cuddle", "lick"]:
            return action + "s"
        elif action in ["kiss", "punch"]:
            return action + "es"
        return action

    async def action(self, *, count: int, action: str, person: discord.Member, target: Union[discord.Member, discord.User]):  # type: ignore
        gif = (await self.client.get(action)).url
        embed: discord.Embed = discord.Embed(color=0xFB5F5F)
        action: str = self.determine_action(action)
        embed.title = f"{person.display_name} {action} {target.display_name}!"
        count = humanize.number.ordinal(count) if count != 0 else None
        action = action.replace("s", "") if action in ("cuddles", "punches") else action
        embed.description = f"This is your {count} {action}!" if count else None
        embed.set_image(url=gif)
        return embed

    async def marry(
        self,
        itr: discord.Interaction,
        *,
        person: discord.Member,
        target: Union[discord.Member, discord.User],
    ):
        print("creating marriage image")
        marry = Marriage(person, target, session=self.client.session)
        file = discord.File(await marry.marry_pic(), filename="marry.png")
        embed: discord.Embed = discord.Embed(
            title=f"{person.display_name} and {target.display_name} are now married!",
            color=0xFB5F5F,
        )
        embed.set_image(url="attachment://marry.png")
        print("completed marriage image")
        return {"embed": embed, "file": file}
