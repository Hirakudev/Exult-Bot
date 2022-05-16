from io import BytesIO
import textwrap
from PIL import Image, ImageDraw
from discord import Member
from easy_pil import Editor, Canvas, Font
from humanize.number import ordinal

from bot import ExultBot


class WelcomeCard:
    def __init__(self, bot):
        self.bot: ExultBot = bot

    async def make_image(self, member: Member):

        async with self.bot.session.get(
            self.bot.try_asset(member.avatar, member.default_avatar)
        ) as img:
            data = await img.read()

        with Image.open(BytesIO(data)) as image:
            background = Editor(Canvas((1080, 400), color="#23272A"))
            image = Editor(image=image).resize((300, 300)).circle_image()
            font = Font.poppins(size=40)
            font_big = Font.poppins(size=50)
            font_text = Font.poppins(size=30)
            background.polygon([(1, 1), (1, 540), (540, 540), (200, 1)], fill="#2C2F33")
            background.polygon([(1, 1), (1, 540), (540, 540), (150, 1)], fill="#484d50")
            draw = ImageDraw.Draw(background.image)
            draw.rounded_rectangle(
                (25, 25, 1055, 375), outline="#f1c40f", width=5, radius=35
            )
            background.rounded_corners(radius=50)
            background.paste(image, (50, 50))

            text = f"Welcome to {member.guild}, {member.name}!"
            position = ordinal(
                sorted([m.joined_at for m in member.guild.members]).index(
                    member.joined_at
                )
                + 1
            )
            text2 = f"You are the {position} member to join!"
            POS_X = 450
            POS_Y = 90
            for line in textwrap.wrap(text, width=30):
                background.text((POS_X, POS_Y), line, font=font, color="#ffffff")
                POS_Y += 40
            background.text((POS_X, 275), text2, font=font_text, color="#ffffff")
            buffer = BytesIO()
            background.image = background.image.resize(
                size=(background.image.size), resample=Image.ANTIALIAS
            )
            background.image.save(buffer, format="PNG")
            buffer.seek(0)
            return buffer
