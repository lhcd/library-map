import time
import json

import requests
import schedule
from bs4 import BeautifulSoup

from nypl_map.models import Library

# TODO: Make this an envar
PULL_PERIOD = 60 * 60

SCRAPE_URL = 'https://refinery.nypl.org/api/nypl/locations/v1.0/locations'
SCRAPE_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
}

def get_data(url, headers={}):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return json.loads(response.content)

def map_library():
    pass

def scrape_nypl_info():
    libraries = get_data(SCRAPE_URL, SCRAPE_HEADERS)
