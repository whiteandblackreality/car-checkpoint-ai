from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor
import requests
from itertools import repeat
import os
import time
from abstract_parser import AbstractParser


class InsecamParser(AbstractParser):

    def parse_one_url(self, url):
        try:
            r = requests.get(url, headers=self.headers)
            soup = bs(r.text, 'html.parser')
            image = soup.find('img', {'id': 'image0'})
            image_link = image['src']
            r = requests.get(image_link).content
            with open(f"{url.split('/')[-1]}/{time.time()}.jpg", "wb+") as f:
                f.write(r)
        except Exception:
            print("Error occured")

    def parse_all_urls(self):
        while True:
            with ThreadPoolExecutor(self.num_pools) as executor:
                results = executor.map(self.parse_one_url, self.url_list)
            time.sleep(self.cooldown)

    def create_folders(self):
        for url in self.url_list:
            folder_name = url.split('/')[-1]
            if not os.path.exists(folder_name):
                os.mkdir(folder_name)


url_filename = "insecam_urls.txt"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 '
                  'Safari/537.36'}

parser = InsecamParser(root_folder="",  # root for folder structure
                       urls=url_filename,  # file with urls or list
                       num_pools=5, # number of threads
                       headers=headers,  # headers for  http request
                       cooldown=5)  # cooldown in seconds

parser.parse_all_urls()
