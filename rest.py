import json
from mock import Mock
from placeholder import Placeholder
from fetchdata import FetchData
from typing import List

INPUT = json.loads("""
[{
    "carrier": "MOCK_INDEMNITY",
    "customerId": "a0dfjw9a"
},{
    "carrier": "PLACEHOLDER_CARRIER",
    "customerId": "f02dkl4e"
}]
""")


class MockRestService:
    Carriers = [Mock, Placeholder]
    Data = {}

    def __init__(self):
        self.scrape()

    def scrape(self):
        """
        Prepare a mock-database by scraping the web pages.
        """
        print('Scrape initiated.')
        fetchers: List[FetchData] = [FetchData(carrier) for carrier in self.Carriers]
        for fetcher in fetchers:
            fetcher.fetch_my_carrier()
            self.Data[fetcher.carrier.system_name] = fetcher
        print('Scrape complete.')

    def respond(self):
        for request in INPUT:
            # Let's assume we expect this format exactly.
            data = self.Data[request['carrier']][request['customer']]


