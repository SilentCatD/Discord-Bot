import requests
from bs4 import BeautifulSoup
import urllib3
import discord
from discord.ext import commands
from discord import Embed
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CovidInfo:
    def __init__(self):
        self.url = 'https://ncov.moh.gov.vn/trang-chu'
        self.response = requests.get(self.url, verify=False)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')

    def _update_info(self):
        self.response = requests.get(self.url, verify=False)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')

    def _separated_stats(self, class_):
        summarize_table = {}
        world = self.soup.find('span', class_=class_).parent
        name = world.text.strip()
        summarize_table[name] = {}
        while world:
            world = world.find_next_sibling('div')
            if world:
                status = world.contents[0].strip()
                numbers = world.contents[3].text.replace('.', ',')
                summarize_table[name][status] = numbers
        return summarize_table

    def summarize_stats(self):
        result = {}
        self._update_info()
        vn_total = self._separated_stats('box-vn')
        world_total = self._separated_stats('box-tg')
        result.update(vn_total)
        result.update(world_total)
        return result

    def provinces_stats(self, limit=5, sort=1):
        # 0: cases
        # 1: today
        # 2:deaths
        self._update_info()
        city_name = ""
        provinces_table = {}
        table = self.soup.find(id='sailorTable')
        city = table.find_all('td')
        for i, element in enumerate(city):
            if i % 4 == 0:
                city_name = element.text
                provinces_table[city_name] = {}
                continue
            value = element.text.replace(".", "")
            if i % 4 == 1:
                provinces_table[city_name]["Tổng số ca"] = int(value)
            elif i % 4 == 2:
                provinces_table[city_name]["Hôm nay"] = int(value)
            elif i % 4 == 3:
                provinces_table[city_name]["Tử vong"] = int(value)

        # Sort
        if sort == 0:
            provinces_table = sorted(provinces_table.items(), key=lambda x: (x[1]['Tổng số ca']), reverse=True)
        elif sort == 1:
            provinces_table = sorted(provinces_table.items(), key=lambda x: (x[1]['Hôm nay']), reverse=True)
        elif sort == 2:
            provinces_table = sorted(provinces_table.items(), key=lambda x: (x[1]['Tử vong']), reverse=True)

        # Limit result
        if limit > 0:
            provinces_table = provinces_table[:limit]
        provinces_table = dict(provinces_table)
        # Format 1000 -> 1,000
        for city in provinces_table:
            for stats in provinces_table[city]:
                provinces_table[city][stats] = '{0:,}'.format(provinces_table[city][stats])
        return provinces_table

    def newest_info(self):
        self._update_info()
        result = {'timeline': {}, 'content': {}}
        newest_timeline = self.soup.find('div', class_='timeline-head')
        newest_content = self.soup.find('div', class_='timeline-content')
        result['timeline'] = newest_timeline.text.strip()
        content = newest_content.text.strip().replace('\xa0', '').split('\n')
        result['content']['cases'] = content[0]
        result['content']['detail'] = content[1]
        return result


class Covid(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def covid(self, ctx, option: str = "", limit: str = "", sort: str = ""):
        info = CovidInfo()
        author_icon = 'https://tptdm.edu.vn/uploads/pgdtptdm/news/2020/logo_byt.png'
        thump_url = 'https://giadinh.mediacdn.vn/thumb_w/640/2020/12/29/anh-chup-man-hinh-2020-12-29-luc-174621-1609238792560568750014.png'
        embed = Embed(title="Thông tin corana virus", url='https://ncov.moh.gov.vn',
                      description="Thông tin được lấy trực tiếp từ trang chủ của bộ y tế Việt Nam",
                      color=discord.Color.blue(),
                      timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=thump_url)
        embed.set_author(name="Bộ y tế", url='https://moh.gov.vn', icon_url=author_icon)
        embed.set_footer(text=f'Information requested by: {ctx.author.display_name}')
        if option == "" and limit == "" and sort == "":
            data = info.summarize_stats()
            async with ctx.message.channel.typing():
                for country in data:
                    text = ""
                    for stat in data[country]:
                        text += f'{stat}: {data[country][stat]}\n'
                    embed.add_field(name=country, value=text, inline=True)
            await ctx.send(embed=embed)
        if option == "today" and limit == "" and sort == "":
            data = info.newest_info()
            async with ctx.message.channel.typing():
                embed.add_field(name="Mốc thời gian: ", value=data['timeline'], inline=False)
                embed.add_field(name=data["content"]["cases"], value=data["content"]["detail"])
            await ctx.send(embed=embed)

        if option == "stat":
            if limit.isdigit() and 10 >= int(limit) > 0:
                limit = int(limit)
            else:
                limit = 6
            if sort.isdigit() and 0 <= int(sort) <= 2:
                sort = int(option)
            else:
                sort = 1
            data = info.provinces_stats(limit, sort)
            async with ctx.message.channel.typing():
                for province in data:
                    text = ""
                    for status in data[province]:
                        text += f'{status}: {data[province][status]}\n'
                    embed.add_field(name=province, value=text)
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Covid(client))
