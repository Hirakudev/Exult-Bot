from discord import Interaction, Webhook, Colour
from discord.app_commands import command, describe
# Discord Imports

from os import environ
from json import loads
#Regular Imports

from utils import *
# Local Imports

class Weather(ExultCog):

    @command(name="weather", description="Get the weather forecast!")
    @describe(destination="The place you want to view weather information on.")
    async def weather_slash(self, itr: Interaction, destination: str):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: Webhook = itr.followup

        url = "https://community-open-weather-map.p.rapidapi.com/weather"
        querystring = {"q": destination, "lat": "0", "lon": "0", "id": "2172797", "lang": "null",
                       "units": "\"metric\" or \"imperial\"", "mode": "xml, html"}
        h = {
            'x-rapidapi-key': environ["RAPIDAPI_KEY"],
            'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com"}
        async with bot.session.get(url, headers=h, params=querystring) as data:
            data = loads(await data.text())
            if data.get("message"):
                embed = embed_builder(description=f"No results found for `{destination}`")
                await followup.send(embed=embed)
            
        feels_like = round(float(data["main"]["feels_like"])  - 273.15, 2)
        temp = round(float(data['main']['temp']) - 273.15, 2)
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
        else:
            colour = Colour.random()

        maxT, minT = round(float(data['main']['temp_max']) - 273.15, 2), round(
            float(data['main']['temp_min']) - 273.15, 2)
        wind = data['wind']
        misc = f"-The current air pressure is {data['main']['pressure']} Pa\n-The Humidity is {data['main']['humidity']}%" \
               f"\n-The Visibility is {int(data['visibility']) / 1000} Km"

        embed = embed_builder(title=f"{data['name']}, {data['sys']['country']}", colour=colour,
                              fields=[
                                  ["Weather", f"-{data['weather'][0]['description']}\n{misc}", False],
                                  ["Wind & Temperature", f"🌡 **{temp}℃** (max: {maxT}℃, min: {minT}℃)\n" \
                                   f"👐 Feels like **{feels_like}℃**\n" \
                                   f"🌬 Wind Speed: **{wind['speed']}mph**", False]
                              ])
        await followup.send(embed=embed)