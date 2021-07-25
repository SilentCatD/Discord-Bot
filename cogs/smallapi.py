import discord
from discord.ext import commands
from discord import Embed
import requests


class SmallAPI(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def covid(self, ctx):
        response = requests.get('https://corona.lmao.ninja/v3/covid-19/all')
        data = response.json()
        thump_url = 'https://disease.sh/assets/img/flags/vn.png'
        async with ctx.message.channel.typing():
            embed = Embed(title='COVID-19', description="Covid information",
                          colour=discord.Color.blue(), timestamp=ctx.message.created_at)
            embed.set_thumbnail(url=thump_url)
            embed.add_field(name="Global", value=f'Today Case: {data["todayCases"]}'
                                                 f' | Total Case: {data["cases"]}\n'
                                                 f'Today Deaths:  {data["todayDeaths"]}'
                                                 f' | Total Deaths {data["deaths"]}\n'
                                                 f'Today recovered: {data["todayRecovered"]}'
                                                 f' | Total recovered: {data["recovered"]}',
                            inline=False)
            response = requests.get("https://corona.lmao.ninja/v3/covid-19/countries/vn?strict=true")
            data = response.json()
            embed.add_field(name="Viet Nam", value=f'Today Case: {data["todayCases"]}'
                                                   f' | Total Case: {data["cases"]}\n'
                                                   f'Today Deaths:  {data["todayDeaths"]}'
                                                   f' | Total Deaths {data["deaths"]}\n'
                                                   f'Today recovered: {data["todayRecovered"]}'
                                                   f' | Total recovered: {data["recovered"]}',
                            inline=False)
            embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command()
    async def weather(self, ctx, *, city: str = ""):
        if city == "":
            await ctx.send(f'Specify a city please!')
            return
        api_key = 'd9dd7595f02577a2bf2b9f385ebc1c64'
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        city_name = city
        complete_url = base_url + "appid=" + api_key + "&q=" + city_name
        response = requests.get(complete_url)
        x = response.json()
        channel = ctx.message.channel
        if x["cod"] != "404":
            async with channel.typing():
                y = x["main"]
                current_temperature = y["temp"]
                current_temperature_celsiuis = str(round(current_temperature - 273.15))
                current_pressure = y["pressure"]
                current_humidity = y["humidity"]
                z = x["weather"]
                weather_description = z[0]["description"]
                weather_description = z[0]["description"]
                embed = discord.Embed(title=f"Weather in {city_name}",
                                      color=ctx.guild.me.top_role.color,
                                      timestamp=ctx.message.created_at, )
                embed.add_field(name="Descripition", value=f"**{weather_description}**", inline=False)
                embed.add_field(name="Temperature(C)", value=f"**{current_temperature_celsiuis}°C**", inline=False)
                embed.add_field(name="Humidity(%)", value=f"**{current_humidity}%**", inline=False)
                embed.add_field(name="Atmospheric Pressure(hPa)", value=f"**{current_pressure}hPa**", inline=False)
                embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
                embed.set_footer(text=f"Requested by {ctx.author.name}")
            await channel.send(embed=embed)
        else:
            await channel.send("City not found.")

    @commands.command()
    async def quote(self, ctx):
        url = 'https://zenquotes.io/api/random'
        response = requests.get(url)
        response = response.json()
        thumbnail_url = "https://cdn.browsercam.com/logos/com.kaydownes.ZenQuotes-logo.png"
        async with ctx.message.channel.typing():
            embed = discord.Embed(title=f"",
                                  color=ctx.guild.me.top_role.color,
                                  timestamp=ctx.message.created_at, description=f'***{response[0]["q"]}***')
            embed.set_thumbnail(url=thumbnail_url)
            embed.set_author(name=f'{response[0]["a"]} used to say')
            embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(SmallAPI(client))
