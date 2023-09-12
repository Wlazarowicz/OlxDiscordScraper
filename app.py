import json
import requests
from bs4 import BeautifulSoup
from discord.ext import tasks
import discord
import asyncio
import os
from colorama import init
from termcolor import colored
from dotenv import load_dotenv

load_dotenv()
init()

TOKEN = os.getenv("TOKEN") ## Your discord bod token
URL = os.getenv("URL") ##olx.pl page to scrap on
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) ##Your discord channel id
offers_from_file = []


def get_latest_items():
    print(colored(f'Scrapping for latest items...', 'cyan'))
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    listings = soup.find_all('div', {'class': 'css-1sw7q4x', 'data-cy': 'l-card'})
    json_object = [] #list of dictionaries
    for listing in listings:
        listing_name = listing.find('h6', {'class': 'css-16v5mdi er34gjf0'}).text;
        listing_price = listing.find('p', {'class': 'css-10b0gli er34gjf0'}).text
        listing_url = "https://olx.pl" + "" + listing.find('a', {'class': 'css-rc5s2u'}).get('href')
        if(listing.find('img', {'class': 'css-8wsg1m'}) is not None):
            if(listing.find('img', {'class': 'css-8wsg1m'}).get('src').startswith('https')):
                listing_image_url = listing.find('img', {'class': 'css-8wsg1m'}).get('src').split(';',1)[0]
        elif(listing.find('img', {'class': 'css-gwhqbt'}) is not None):
            if(listing.find('img', {'class': 'css-gwhqbt'}).get('src').startswith('https')):
                listing_image_url = listing.find('img', {'class': 'css-gwhqbt'}).get('src').split(';',1)[0]
        listing_date = listing.find('p', {'class': 'css-veheph er34gjf0'}).text
        listing_quality = listing.find('span', {'class': 'css-3lkihg'}).text
        ##console.log(listing_image_url)
        json_scheme = {
        "url": listing_url,
        "name": listing_name,
        "price": listing_price,
        "date": listing_date,
        "image": listing_image_url,
        "quality": listing_quality
}
        json_object.append(json_scheme)
    return process_json_object(json_object)


def process_json_object(json_object):
    with open('items.json', 'r', encoding='utf-8') as f:
        global local_items
        local_items = json.load(f) #list of dictionaries
        print(colored(f'Local items loaded', 'green'))
        unique_items = []
        for dict_ in json_object:
            found_match = False
            for dict2_ in local_items:
                if dict_["url"] == dict2_["url"]:
                    found_match = True
            if not found_match:
                unique_items.append(dict_)
                #console.log(dict_)
                local_items.append(dict_)
    with open('items.json', 'w', encoding='utf-8') as f:
        json.dump(local_items, f, ensure_ascii=False, indent=4)
    
    return unique_items


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def my_background_task(self):
        await client.wait_until_ready()
        channel = client.get_channel(CHANNEL_ID)
        while not client.is_closed():
            latest_items = get_latest_items()
            for item in latest_items:
                embed=discord.Embed(title=item['name'], url=item['url'], description=item['quality'] + '                     ' + item['price'])
                embed.set_author(name='olx.pl', icon_url='https://static.olx.pl/static/olxpl/naspersclassifieds-regional/olxeu-atlas-web-olxpl/static/img/fb/fb-image_redesign.png')
                ##embed.set_thumbnail(url=item['image'])
                embed.set_footer(text=item['date'])
                ##await channel.send(embed=embed)
            await asyncio.sleep(7200)  # task runs every 2 hours

    async def on_ready(self):
        print(colored(f'Logged in as {self.user}', 'green'))
        print(colored(f'------\n', 'green'))
client = MyClient(intents=discord.Intents.default())
client.run(TOKEN)