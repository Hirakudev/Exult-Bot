[Temp PIL functions]
import asyncio
from io import BytesIO
from typing import (Union)

from PIL import Image, ImageDraw, ImageOps
import aiohttp
from easy_pil import Editor, Canvas, Font
import discord
@bot.command(name='uwu',)
async def rankcard(ctx, rank, level, xp, xp_total):
  async def get_avatar(user: discord.Member = ctx.author):
    async with bot.session.get(user.avatar.url) as resp:
      data = await resp.read()
      return [data, str(user)]
  def rank_card(data ,level: int, rank: Union[int,str], xp: int, xp_total = int) -> BytesIO:
      with Image.open(BytesIO(data[0])) as image:
          background = Editor(Canvas((1080, 400), color="#23272A"))
          image = Editor(image=image).resize((300,300)).circle_image()
          font = Font.poppins(size=40)
          font_big = Font.poppins(size=50)
          font_text = Font.poppins(size=30)
          font_small = Font.poppins(size=20)
          background.polygon([(1, 1), (1, 540), (540, 540), (200, 1)],fill='#2C2F33')
          background.polygon([(1, 1), (1, 540), (540, 540), (150, 1)],fill='#484d50')
          draw = ImageDraw.Draw(background.image)
          draw.rounded_rectangle((25, 25, 1055, 375), outline="#fb5f5f", width=5, radius=35)
          draw.rounded_rectangle((490, 240, 958, 300), outline="#ffffff", width=5, radius=100)
          background.rounded_corners(radius=50)
          
          background.text(position=(825, 210), text=f"{xp} / {xp_total} XP", font=font_small, color="#ffffff")
          background.text(position=(500,205),text=str(data[1]),font=font_text,color="#9D9D9E")
          background.paste(image, (50, 50))
          background.text(position=(550,75),text=f"Rank ",color="#ffffff",font=font)
          background.text(position=(650,70),text=f"#{rank}",color="#fb5f5f",font=font_big)
          background.text(position=(800,75),text=f"Level",color="#ffffff",font=font)
          background.text(position=(900,70),text=f" {level}",color="#fb5f5f",font=font_big)
          percent = round((xp/xp_total)*100)
          background.bar((500, 250),max_width=650,height=40,percentage=int(percent),fill="#fb5f5f",radius=30,)
          buffer = BytesIO()
          background.image = background.image.resize(size = (background.image.size),resample=Image.ANTIALIAS)
          background.image.save(buffer, format="PNG")
          buffer.seek(0)
          return buffer
        
  data = await get_avatar(ctx.author)
  fp = rank_card(data=data,level=level,rank=rank,xp=int(xp),xp_total=int(xp_total))
  await ctx.send(file=discord.File(fp=fp,filename='rank.png'))
