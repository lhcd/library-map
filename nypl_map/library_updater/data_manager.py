import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from nypl_map.models import Library, LastRefreshed
from nypl_map.library_updater.mappers import api_library_to_orm_library


# TODO: Make this an envar
PULL_PERIOD = 60 * 60

SCRAPE_URL = 'https://refinery.nypl.org/api/nypl/locations/v1.0/locations'
SCRAPE_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
}

class DataManager():
    def get_data(self, url, headers={}):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def scrape_nypl_info(self):
        print('Scraping NYPL')
        data = self.get_data(SCRAPE_URL, SCRAPE_HEADERS)
        self.update_dataset(data)

    def update_dataset(self, dataset: dict):
        refresh_record = LastRefreshed.objects.get_or_create(defaults={
            'refresh_time': datetime.now()
        })

        for library in dataset.get('locations', {}):
            Library.get_or_update_by_nypl_id(api_library_to_orm_library(library))