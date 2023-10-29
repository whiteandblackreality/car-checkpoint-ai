from abc import ABC, abstractmethod
from typing import Union, List


class AbstractParser(ABC):

    def __init__(self, root_folder: str, urls: Union[str, List[str]], num_pools: int, headers: dict, cooldown: int):
        self.root_folder = root_folder
        self.num_pools = num_pools
        self.headers = headers
        self.cooldown = cooldown
        self.urls = urls
        if isinstance(urls, str):
            self.url_list = self.read_urls_from_file()
        else:
            self.url_list = self.urls
        self.create_folders()

    def read_urls_from_file(self):
        with open(self.urls, "r") as url_file:
            urls = url_file.read().splitlines()
        return urls

    @abstractmethod
    def create_folders(self):
        pass

    @abstractmethod
    def parse_one_url(self, url):
        pass

    @abstractmethod
    def parse_all_urls(self):
        pass
