from discord import app_commands, Interaction, Object, Colour
from discord.ext.commands import Cog, Bot

import os
import requests as r
from bs4 import BeautifulSoup
import json
import random

from utils import * 

class Fun(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.dagpi_token = os.getenv("DAGPI_TOKEN")
        self.HEADER = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, '
                        'like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53.'}
        self.FONT = {'q': '𝗾', 'w': '𝘄', 'e': '𝗲', 'r': '𝗿', 't': '𝘁', 'y': '𝘆', 'u': '𝘂', 'i': '𝗶', 'o': '𝗼', 'p': '𝗽',
        'a': '𝗮', 's': '𝘀', 'd': '𝗱', 'f': '𝗳',
        'g': '𝗴', 'h': '𝗵', 'j': '𝗷', 'k': '𝗸', 'l': '𝗹', 'z': '𝘇', 'x': '𝘅', 'c': '𝗰', 'v': '𝘃', 'b': '𝗯',
        'n': '𝗻', 'm': '𝗺'}
        super().__init__()
        
    def convertSoup(self, link, user_agent=None):
        if not user_agent:
            user_agent = self.HEADER
        if user_agent:
            return BeautifulSoup(r.get(link, headers=user_agent, timeout=5).content, 'html.parser')
        page = r.get(link, timeout=5)
        return BeautifulSoup(page.content, 'html.parser')
    
    def accuracy(self, sentence, userInput):
        words = sentence.split()
        sentence = ''.join(words)
        userInput = userInput.split()
        correct = 1
        for i in range(len(words)):
            try:
                for a in range(len(words[i])):
                    try:
                        correct += 0 if words[i][a] != userInput[i][a] else 1
                    except IndexError:
                        break
            except IndexError:
                break
        return round(correct / len(sentence) * 100, 2)
    
    def convertFont(self, string):
        new = ''
        for char in string:
            if char in self.FONT:
                new += self.FONT[char]
            elif char.isupper() and char.lower() in self.FONT:
                new += self.FONT[char.lower()].upper()
            else:
                new += char
        return new

    @app_commands.command(name="wtp", description="Who's that pokemon?")
    async def wtp_slash(self, interaction: Interaction):
        headers = {"Authorization": self.dagpi_token}
        res = r.get("https://api.dagpi.xyz/data/wtp", headers=headers).json()
        
        question = res["question"]
        answer = res["answer"]
        name = res["Data"]["name"]
        types = ", ".join(res["Data"]["Type"])
        data = {"name": name, 
                "question": question, 
                "answer": answer, 
                "types": types,
                "lives": 3} 
        embed = embed_builder(title="Who's that pokemon?", description=f"Type(s): {types}", image=question, 
                            fields=[["Guesses Remaining:", str(data["lives"]), True]],
                            footer=name)
        view = PokemonGuess(data)
        await interaction.response.send_message(embed=embed, view=view)
        
    @app_commands.command(name="joke", description="Get a joke")
    async def joke_slash(self, interaction: Interaction):
        headers = {'Authorization': self.dagpi_token}
        res = r.get('https://api.dagpi.xyz/data/joke', headers=headers).json()
        embed = embed_builder(description=res["joke"])
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="roast", description="Get Roasted")
    async def roast_slash(self, interaction: Interaction):
        headers = {'Authorization': "MTYzMTg3Mzk4Nw.VIpkBtkBNQRy1AWV8GZ08OFhEWSGUK8D.071b411fc46ce97f"}
        res = r.get('https://api.dagpi.xyz/data/roast', headers=headers).json()
        embed = embed_builder(description=res["roast"])
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="fact", description="Get a fact")
    async def fact_slash(self, interaction: Interaction):
        fact_html = self.convertSoup("http://randomfactgenerator.net")
        fact = fact_html.find('div', id="z").text
        embed = embed_builder(description=fact.split("\n")[0])
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="weather", description="Get weather info on a certain area")
    @app_commands.describe(place="The place you want to view weather statistics on")
    async def weather_slash(self, interaction: Interaction, place: str):
        url = "https://community-open-weather-map.p.rapidapi.com/weather"
        querystring = {"q": place, "lat": "0", "lon": "0", "id": "2172797", "lang": "null",
                       "units": "\"metric\" or \"imperial\"", "mode": "xml, html"}
        h = {
            'x-rapidapi-key': "c97af16bb5msh4a9c4bd102924e7p13f694jsna81d3f25137a",
            'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com"
        }
        response = json.loads(r.request("GET", url, headers=h, params=querystring).text)
        if response.get('message'):
            await interaction.response.send_message(embed=embed_builder(description=f"No results found for `{place}`"))
        feels_like = round(float(response['main']['feels_like']) - 273.15, 2)
        temp = round(float(response['main']['temp']) - 273.15, 2)
        if temp < -30:
            colour = Colour.dark_blue()
        elif temp >= -29 and temp <= 0:
            colour = Colour.blue()
        elif temp >= 1 and temp <= 9:
            colour = 0xADD8E6
        elif temp >= 10 and temp <= 19:
            colour = Colour.green()
        elif temp >= 20:
            colour = Colour.dark_gold()
        maxT, minT = round(float(response['main']['temp_max']) - 273.15, 2), round(
            float(response['main']['temp_min']) - 273.15, 2)
        wind = response['wind']
        misc = f"-The current air pressure is {response['main']['pressure']} Pa\n-The Humidity is {response['main']['humidity']}%" \
               f"\n-The Visibility is {int(response['visibility']) / 1000} Km"
        embed = embed_builder(title=f"{response['name']}, {response['sys']['country']}", colour=colour,
                              fields=[
                                  ["Weather", f"-{response['weather'][0]['description']}\n{misc}", False],
                                  ["Wind & Temperature", f"🌡 **{temp}℃** (max: {maxT}℃, min: {minT}℃)\n👐 Feels like **{feels_like}℃**\n" \
                                   f"🌬 Wind Speed: **{wind['speed']}mph**", False]
                              ])
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="animal", description="Get a random animal")
    async def animal_slash(self, interaction: Interaction):
        soup = self.convertSoup('https://www.bestrandoms.com/random-animal-generator', self.HEADER)
        animals = soup.findAll(class_='text-center')
        image = 'https://www.bestrandoms.com' + animals[2].find('img')['src']
        name = animals[2].find('img')['alt'].replace('logo', '')
        phrases = [f'The {name}', f'A fine looking {name}', f'A very lovely {name}']
        desc = animals[4].text
        embed = embed_builder(title=random.choice(phrases).replace('  ', ' '), footer=desc, image=image)
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="meme", description="Get a random meme")
    async def meme(self, interaction: Interaction):
        async with self.bot.session.get("https://reddit.com/r/memes/random.json") as req:
            data = await req.json()
            post = data[0]['data']['children'][0]['data']
            embed = embed_builder(title=post['title'], image=post['url_overridden_by_dest'])
            await interaction.response.send_message(embed=embed)

async def setup(bot: Bot):
    await bot.add_cog(Fun(bot), guilds=[Object(guild) for guild in bot.app_guilds])