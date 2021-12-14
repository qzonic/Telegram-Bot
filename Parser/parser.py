import requests
from bs4 import BeautifulSoup
import re
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 YaBrowser/20.4.1.223 Yowser/2.5 Safari/537.36',
           'accept': '*/*'
           }

class MainParser:
    def __init__(self, game):
        self.game = game


    def get_html(self, url):
        req = requests.get(url, headers=HEADERS, params=None, verify=False)

        return req

    def parse(self):
        xml = self.get_html(url=self.URL)
        if xml.status_code == 200:
            rez = self.get_content(xml.text)
            return rez
        else:
            return "Сервер не отвечает"

    def get_content(self, xml):
        lister = []
        soup = BeautifulSoup(xml, "lxml")
        for item in soup.find_all(self.prod):
            if re.search(re.sub("[!@#^'$:]", '', self.game).lower(), re.sub("[!@#^'$:]", '', item.find("name").get_text(strip=True)).lower()):
                name = item.find("name").get_text(strip=True)
                price = int(item.find("price").get_text(strip=True))
                url = item.find("url").get_text(strip=True) + self.ref
                lister.append([name, price, url])
        return lister


class SteamPayParser(MainParser):
    URL = 'https://api.steampay.com/api/products'
    ref = '/?agent=12a2b502-0b76-4333-be18-99684c48b06c'

    def __init__(self, game):
        self.game = game

    def parse(self):
        html = self.get_html(self.URL)
        if html.status_code == 200:
            rez = self.get_content(html.text)
            return rez
        else:
            return "Сервер не отвечает"

    def get_content(self, html):
        lister = []
        soup = json.loads(str(BeautifulSoup(html, 'html.parser')))
        for item in soup["products"]:
            if re.search(re.sub("[!@#^'\"$:]", '', self.game).lower(), re.sub("[!@#^'\"$:]", '', item["title"].lower())):
                name = item["title"]
                price = item['prices']['rub']
                url = item['url']+self.ref
                lister.append([name, price, url])
        return lister

class SteamAccountParser(MainParser):
    URL = 'https://steam-account.ru/partner/products.xml'
    ref = '?ai=1027734'
    prod = "product"

class ZakaZakaParser(MainParser):
    URL = "https://feed.zaka-zaka.com/api/getlist/type/xml/"
    ref = '/?agent=32c98f89-dbde-484e-9608-98af4a219575'
    prod = "offer"

class SteamBuyParser(MainParser):
    URL = "http://steammachine.ru/api/goodslist/?v=1&format=xml"
    ref = "partner/1027734"
    prod = "goods"

    def parse(self):
        xml = self.get_html(url=self.URL)
        if xml.status_code == 200:
            rez = self.get_content(xml.text)
            return rez
        else:
            return "Сервер не отвечает"

    def get_content(self, xml):
        lister = []
        soup = BeautifulSoup(xml, 'lxml')
        for item in soup.find_all(self.prod):
            if item.find("available").get_text(strip=True) == "1":
                if re.search(re.sub("[!@#^'$:]", '', self.game).lower(), re.sub("[!@#^'$:]", '', item.find("name").get_text(strip=True)).lower()):
                    name = item.find("name").get_text(strip=True)
                    price = int(item.find("price").get_text(strip=True))
                    url = item.find("url").get_text(strip=True) + self.ref
                    lister.append([name, price, url])
        return lister


