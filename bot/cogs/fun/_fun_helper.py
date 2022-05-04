import os
from bs4 import BeautifulSoup

from bot import ExultBot
from utils import *

class FunHelper:
    def __init__(self, bot: ExultBot):
        self.bot: ExultBot = bot
    HEADER = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, '
                        'like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53.'}
    dagpi_token = os.environ["DAGPI_TOKEN"]

    async def convertSoup(self, link, user_agent=None):
        if not user_agent:
            user_agent = self.HEADER
        async with self.bot.session.get(link, headers=user_agent, timeout=5) as data:
            return BeautifulSoup(data.content, 'html.parser')