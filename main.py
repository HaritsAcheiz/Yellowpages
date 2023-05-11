import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


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
        stage1 = soup.select('script')
        print(len(stage1))

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
    s.parse(html)