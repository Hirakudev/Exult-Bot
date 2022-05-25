import discord

import aiohttp
import io
from PIL import Image, ImageDraw, ImageChops, ImageOps
from typing import Optional, Union

from bot import ExultBot


class Marriage:
    def __init__(
        self,
        person: discord.Member,
        target: Union[discord.Member, discord.User],
        session: Optional[aiohttp.ClientSession] = None,
    ):
        self.person: discord.Member = person
        self.target: Union[discord.Member, discord.User] = target
        self.session = session if session else None

    async def download_avatar(
        self, thing: Union[discord.Member, discord.User]
    ) -> io.BytesIO:
        self.session = self.session if self.session else aiohttp.ClientSession()
        resp = await self.session.get(thing.display_avatar.url)  # type: ignore
        _resp = await resp.read()
        return io.BytesIO(_resp)

    async def circle(self, user: Union[discord.Member, discord.User]) -> Image.Image:
        resp: io.BytesIO = await self.download_avatar(user)
        with Image.open(resp) as image:
            base = Image.new("RGBA", size=image.size, color=(0, 0, 0, 0))
            size_circle = (image.size[0] * 3, image.size[1] * 3)
            mask = (
                Image.open("utils/image_gen/mask.png")
                .resize(size_circle, Image.ANTIALIAS)
                .convert("L")
            )
            ImageDraw.Draw(mask).ellipse((0, 0) + size_circle, fill=254)
            mask = mask.resize(image.size, Image.ANTIALIAS)
            mask = ImageChops.darker(mask, image.split()[-1])
            image = ImageOps.fit(image=image, size=mask.size, centering=(0.7, 0.7))
            base.paste(image, (0, 0), mask=mask)
            final = base.resize((700, 700))
            return final

    async def marry_pic(self) -> io.BytesIO:
        base = Image.open("utils/image_gen/base.png")
        heart = Image.open("utils/image_gen/heart-1.png")
        person = await self.circle(self.person)
        target = await self.circle(self.target)

        base.paste(person, (200, 100), person)
        base.paste(target, (1050, 100), target)
        base.paste(heart, (675, 200), heart)
        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
