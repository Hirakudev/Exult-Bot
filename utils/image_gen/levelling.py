from io import BytesIO
from PIL import Image, ImageDraw
from easy_pil import Editor, Canvas, Font

from bot import ExultBot


class RankCard:
    def __init__(self, bot):
        self.bot: ExultBot = bot

    async def make_image(self, member, data):
        xp = data.get("xp")
        required_xp = data.get("required_xp")
        rank = data.get("rank")
        level = data.get("level")
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
            font_small = Font.poppins(size=20)
            background.polygon([(1, 1), (1, 540), (540, 540), (200, 1)], fill="#2C2F33")
            background.polygon([(1, 1), (1, 540), (540, 540), (150, 1)], fill="#484d50")
            draw = ImageDraw.Draw(background.image)
            draw.rounded_rectangle(
                (25, 25, 1055, 375), outline="#fb5f5f", width=5, radius=35
            )
            draw.rounded_rectangle(
                (490, 240, 958, 300), outline="#ffffff", width=5, radius=100
            )
            background.rounded_corners(radius=50)
            background.text(
                position=(825, 210),
                text=f"{xp} / {required_xp} XP",
                font=font_small,
                color="#ffffff",
            )
            background.text(
                position=(500, 205), text=str(member), font=font_text, color="#9D9D9E"
            )
            background.paste(image, (50, 50))
            background.text(
                position=(550, 75), text=f"Rank ", color="#ffffff", font=font
            )
            background.text(
                position=(650, 70), text=f"#{rank}", color="#fb5f5f", font=font_big
            )
            background.text(
                position=(800, 75), text=f"Level", color="#ffffff", font=font
            )
            background.text(
                position=(900, 70), text=f" {level}", color="#fb5f5f", font=font_big
            )
            percent = round((xp / required_xp) * 100)
            background.bar(
                (500, 250),
                max_width=450,
                height=40,
                percentage=int(percent),
                fill="#f1c40f",
                radius=30,
            )
            buffer = BytesIO()
            background.image = background.image.resize(
                size=(background.image.size), resample=Image.ANTIALIAS
            )
            background.image.save(buffer, format="PNG")
            buffer.seek(0)
            return buffer
