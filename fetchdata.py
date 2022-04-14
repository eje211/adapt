import urllib.request

import lxml.html

from carrier import Carrier
from customtypes import Customer
from lxml.html.soupparser import fromstring


class FetchData:
    def __init__(self, carrier: Carrier):
        self.carrier = carrier
        self.uri = self.carrier.URI

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
        self.carrier.tree = self.uri_to_xpath(self.uri)

    def scrape_unique_item(self, cls):
        """
        Scrapes an item that is unique within an entry, as opposed to iterated items.
        Given that the data can be different from one carrier to the next, if Python were really used,
        it would be a good idea to use keyword attribute rather than placed attributes.
        :param cls: The type of the item to return.
        :return: An object representing the scraped data.
        """
        fields = []
        for field in cls:
            indexed_xpath = self.carrier.customer_xpath[field]
            node = self.carrier.tree.xpath(indexed_xpath.xpath)
            text = None
            if isinstance(node, list):
                text = node[indexed_xpath.place]
            elif isinstance(node, str):
                text = node
            if text:
                fields.append(Customer.types[field](text))
        return cls(*fields)

    def scrape_policies(self):
        self.get_root()
        for policy in list(self.carrier.fetch_policies(self.carrier.tree, self.carrier.POLICIES)):
            yield policy
