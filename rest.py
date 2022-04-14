import json
from mock import Mock
from placeholder import Placeholder
from fetchdata import FetchData
from typing import List
from json import JSONEncoder
from typing import Mapping, List

INPUT: List[Mapping[str, str]] = json.loads("""
[{
    "carrier": "MOCK_INDEMNITY",
    "customerId": "a0dfjw9a"
},{
    "carrier": "PLACEHOLDER_CARRIER",
    "customerId": "f02dkl4e"
}]
""")


class MockRestService:
    """
    A mock, very approximate REST service, that will take in the given input and use it to return
    the appropriate JSON after scraping a fresh copy of the data.
    """
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
        """
        Get JSON from the given input.
        This is really a dummy function. It does not accept just any
        REST input, just the expected input, as the parameters of how
        real input would arrive are currently unknown.
        :return: JSON in string format.
        """
        customer = {}
        for request in INPUT:
            # Let's assume we expect this format exactly.
            customer[request['carrier']] = {}
            customer_carrier = customer[request['carrier']]
            customer_carrier[request['customerId']] =\
                self.Data[request['carrier']].customers[request['customerId']].to_dict()
        return self.make_json(customer)

    @staticmethod
    def make_json(data: dict):
        """
        Converts a Python-serializable object into JSON text.
        :param data: A Python-serializable object.
        :return: A string that contains a JSON object.
        """
        return JSONEncoder(indent=4).encode(data)

