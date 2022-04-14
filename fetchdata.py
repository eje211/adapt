import urllib.request

import lxml.html

from carrier import Carrier, Policy
from customtypes import Customer, Agent
from lxml.html.soupparser import fromstring
from typing import Type, List


class FetchData:

    def __init__(self, carrier: Type[Carrier]):
        self.carrier = carrier
        self.uri = self.carrier.URI
        self.data = {}
        self.customers = {}
        self.agents = {}
        self.policies = {}

    def fetch_my_carrier(self):
        """
        Scrape all the data for the loaded agency and store it in this instance.
        """
        self.get_root()
        print(f'Getting customer data for {self.carrier.name} ...')
        self.data['customer_data']: Customer = self.scrape_unique_item(Customer, 'customer')
        print(f'Getting agent data for {self.carrier.name} ...')
        self.data['agent_data']: Agent = self.scrape_unique_item(Agent, 'agent')
        # Let's link the customer with the agent and policies here.
        print(f'Getting policy data for {self.carrier.name} ...')
        self.data['policy_data']: List[Type[Policy]] = self.scrape_policies()
        print('Aggregating...')

        # We're in a non-relational database context anyway.
        self.data['customer_data'].agent = self.data['agent_data']
        self.data['customer_data'].policies = self.data['policy_data']

        self.customers[self.data['customer_data'].id] = self.data['customer_data']
        self.agents[self.data['agent_data'].producer_code] = self.data['agent_data']
        for policy in self.data['policy_data']:
            self.policies[policy.id] = policy
        self.data['customer_data'].policies = self.policies
        print(f'All the data for the carrier {self.carrier.name} has been scraped and aggregated.')

    @staticmethod
    def encoding() -> str:
        """
        Future support for other encodings may be added later.
        """
        return 'utf-8'

    @staticmethod
    def uri_to_xpath(uri: str) -> lxml.html.HtmlElement:
        """
        Given a URI, fetch its content and turn it into a searchable XML tree.
        :param uri: The URI to fetch.
        :return: The destination of the URI as a searchable XML tree.
        """
        response = urllib.request.urlopen(uri)
        source = response.read().decode(FetchData.encoding())
        return fromstring(source)

    def get_root(self):
        """
        Fetch the raw HTML text specified by this carrier's URI. Turn into a tree usable by XPath.
        Set the value to the "tree" member of this instance.
        """
        if self.carrier.tree is not None:
            return
        self.carrier.tree = self.uri_to_xpath(self.uri)

    def scrape_unique_item(self, cls, data_point: str) -> List:
        """
        Scrapes an item that is unique within an entry, as opposed to iterated items.
        Given that the data can be different from one carrier to the next, if Python were really used,
        it would be a good idea to use keyword attribute rather than placed attributes.
        :param cls: The type of the item to return.
        :param data_point: The type of top-level data to get, "agent" or "customer".
        :return: An object representing the scraped data.
        """
        fields = []
        data_point += '_xpath'
        for field in cls.Fields:
            try:
                indexed_xpath = getattr(self.carrier, data_point)[field]
            except KeyError:
                print(f'missing: {field}')
                continue
            node = self.carrier.tree.xpath(indexed_xpath.xpath)
            text = None
            if isinstance(node, list):
                text = node[indexed_xpath.place]
            elif isinstance(node, str):
                text = node
            if text:
                fields.append(cls.types[field](text))
        return cls(*fields)

    def scrape_policies(self) -> List[Type[Policy]]:
        """
        Get all the policy object from the current carrier.
        :return:  A list of policy objects.
        """
        self.get_root()
        for policy in self.carrier.fetch_policies(self.carrier.tree, self.carrier.POLICIES):
            yield policy
