import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
import json
import re
from typing import Dict
import csv
import os

@dataclass
class Company:
    name: str
    address: Dict[str,str]
    phone: str
    email: str
    website: str
    detail: str

@dataclass
class YPScraper:

    def get_proxy(self):
        print("Collecting proxies...")
        with requests.Session() as s:
            response = s.get('https://free-proxy-list.net/')
        soup = BeautifulSoup(response.text, 'html.parser')
        list_data = soup.select('table.table.table-striped.table-bordered>tbody>tr')
        scraped_proxies = []
        blocked_cc = ['IR', 'RU']
        for i in list_data:
            ip = i.select_one('tr > td:nth-child(1)').text
            port = i.select_one('tr > td:nth-child(2)').text
            cc = i.select_one('tr > td:nth-child(3)').text
            if cc in blocked_cc:
                continue
            else:
                scraped_proxies.append(f'{ip}:{port}')
        print(f"{len(scraped_proxies)} proxies collected")
        return scraped_proxies

    # Choose working proxy from scraped proxy
    def check_proxy(self,scraped_proxy):
        print(f'checking {scraped_proxy}...')
        formated_proxy = {
            "http": f"http://{scraped_proxy}",
            "https": f"http://{scraped_proxy}"
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        }
        try:
            with requests.Session() as session:
                response = session.get(url='https://www.yellowpages.com.au/', proxies=formated_proxy, headers=headers,
                                       timeout=(7, 10), allow_redirects=False)
            if response.status_code == 200:
                print(f'{scraped_proxy} selected')
                result = scraped_proxy
                return result
            else:
                print(f"not working with status code: {response.status_code}")
        except Exception as e:
            print(f"not working with {e}")

    def fetch(self, url, proxy):
        formated_proxy = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0'
        }

        with requests.Session() as s:
            r = s.get(url, proxies=formated_proxy, headers=headers)
        return r.text

    def parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.select('script')
        json_data = json.loads(re.search(r'({.+})', scripts[2].text).group())
        json_formatted_str = json.dumps(json_data, indent=2)
        print(json_formatted_str)
        items = []
        i = 0
        while 1:
            try:
                name = json_data['model']['inAreaResultViews'][i]['name']
                address = json_data['model']['inAreaResultViews'][i]['primaryAddress']
                phone = json_data['model']['inAreaResultViews'][i]['callContactNumber']['value']
                email = json_data['model']['inAreaResultViews'][i]['primaryEmail']
                website = json_data['model']['inAreaResultViews'][i]['website']
                detail = json_data['model']['inAreaResultViews'][i]['detailsLink']
                items.append(asdict(Company(name=name, address=address, phone=phone, email=email, website=website, detail=detail)))
                i += 1
            except Exception as e:
                print(e)
                break
        return items

    def to_csv(self, datas, filename):
        try:
            for data in datas:
                try:
                    file_exists = os.path.isfile(filename)
                    with open(filename, 'a', encoding='utf-16') as f:
                        headers = ['name', 'address', 'phone', 'email', 'website', 'detail']
                        writer = csv.DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=headers)
                        if not file_exists:
                            writer.writeheader()
                        if data != None:
                            writer.writerow(data)
                        else:
                            pass
                except Exception as e:
                    print(e)
                    continue
        except:
            pass


if __name__ == '__main__':
    url = 'https://www.yellowpages.com.au/search/listings?clue=Property+Manager&locationClue=0830&lat=&lon='
    proxy = '103.69.108.78:8191'
    s = YPScraper()
    # scraped_proxies = s.get_proxy()
    # print(scraped_proxies)
    # working_proxies = []
    # for proxy in scraped_proxies:
    #     working_proxies.append(s.check_proxy(proxy))
    # print(working_proxies)
    html = s.fetch(url, proxy=proxy)
    result = s.parse(html)
    print(result)
    s.to_csv(result,'result.csv')