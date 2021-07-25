import requests
from bs4 import BeautifulSoup
import urllib3

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

    def provinces_stats(self, limit=0, sort=1):
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
        result = {}
        newest_timeline = self.soup.find('div', class_='timeline-head')
        newest_content = self.soup.find('div', class_='timeline-content')
        result['timeline'] = newest_timeline.text.strip()
        content = newest_content.text.strip()
        result['content'] = content.replace('\xa0', '')
        return result