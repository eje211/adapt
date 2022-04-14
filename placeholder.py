from carrier import Carrier, Policy
from decimal import *
from customtypes import PolicyFields, Status, Agent, Customer, IndexedXpath
from typing import ClassVar, Mapping, List, Callable, Generator
from datetime import date
import lxml.html
from dataclasses import dataclass


@dataclass
class PlaceholderPolicy(Policy):
    """
    Information and details about a single policy.
    """

    id: str
    premium: Decimal  # it's a very bad idea to count money with floats.
    status: Status
    effective_date: str
    effective_date: date
    termination_date: date
    last_payment_date: date
    commission_rate: Decimal
    number_of_insured: int

    used_fields: ClassVar[List[PolicyFields]] = [
        PolicyFields.Id, PolicyFields.Premium, PolicyFields.Status,
        PolicyFields.EffectiveDate, PolicyFields.TerminationDate,
        PolicyFields.LastPaymentDate, PolicyFields.CommissionRate,
        PolicyFields.NumberOfInsured
    ]

    data_types: ClassVar[Mapping[PolicyFields, Callable]] = {
        PolicyFields.Id: str,
        PolicyFields.Premium: Decimal,
        PolicyFields.Status: Status.__getitem__,
        PolicyFields.EffectiveDate: Carrier.us_date,
        PolicyFields.TerminationDate: Carrier.us_date,
        PolicyFields.LastPaymentDate: Carrier.us_date,
        PolicyFields.CommissionRate: Carrier.to_decimal,
        PolicyFields.NumberOfInsured: int
    }

    policy_xpath: ClassVar[Mapping[PolicyFields, IndexedXpath]] = {
        PolicyFields.Id:
            IndexedXpath('//td/text()', 0),
        PolicyFields.Premium:
            IndexedXpath('//td/text()', 1),
        PolicyFields.Status:
            IndexedXpath('//td/text()', 2),
        PolicyFields.EffectiveDate:
            IndexedXpath('//td/text()', 3),
        PolicyFields.TerminationDate:
            IndexedXpath('//td/text()', 4),
        PolicyFields.LastPaymentDate:
            IndexedXpath('substring((//td[@class="details-row"]/div/text()), 19)', 2),
        PolicyFields.CommissionRate:
            IndexedXpath('substring((//td[@class="details-row"]/div/text())[2], 15)', 0),
        # Only works up to two digits. A type function can be made to handle more:
        PolicyFields.NumberOfInsured:
            IndexedXpath('substring((//td[@class="details-row"]/div/text())[3], 20)', 0),
    }


class Placeholder(Carrier):
    """
    The implementation of the Placeholder Carrier.
    This carrier uses simple pages with no frames, no JavaScript.
    Every policy is one its own page for each client.
    """

    name = "Placeholder Insurance"

    system_name = 'PLACEHOLDER_CARRIER'

    URI = 'https://scraping-interview.onrender.com/placeholder_carrier/f02dkl4e/policies/1'

    POLICIES = '//tr[contains(@class, "policy-info-row")]'

    policy_type = PlaceholderPolicy

    agent_xpath: Mapping[Agent.Fields, IndexedXpath] = {
        Agent.Fields.Name:
            IndexedXpath('//label[@for="name"]/following-sibling::span/text()', 0),
        Agent.Fields.ProducerCode:
            IndexedXpath('//label[@for="producerCode"]/following-sibling::span/text()', 0),
        Agent.Fields.AgencyName:
            IndexedXpath('//label[@for="agencyName"]/following-sibling::span/text()', 0),
        Agent.Fields.AgencyCode:
            IndexedXpath('//label[@for="agencyCode"]/following-sibling::span/text()', 0),
    }

    customer_xpath: Mapping[Customer.Fields, IndexedXpath] = {
        Customer.Fields.Name:
            IndexedXpath('//label[@for="name"]/following-sibling::span/text()', 1),
        Customer.Fields.Id:
            IndexedXpath('//div[contains(@class, "customer-details")]//span/text()', 1),
        Customer.Fields.Email:
            IndexedXpath('//div[contains(@class, "customer-details")]/div[@class="card-body"]/text()', 0),
        Customer.Fields.Address:
            IndexedXpath('substring(//div[contains(@class, "customer-details")]/div[contains(@class, "card-body")]/'
                         'div[4]/text(), 10)', 0),
        Customer.Fields.SSN:
            IndexedXpath('//div[contains(@class, "customer-details")]/div[contains(@class, "card-body")]/'
                         'div[@style="display:none"]//text()', 1),
    }

    @classmethod
    def host(cls) -> str:
        uri = cls.URI.split('/')[:3]
        uri = '/'.join(uri)
        return uri

    @classmethod
    def fetch_on_this_page(cls, node) -> Generator[lxml.html.HtmlElement, None, None]:
        for policy in node.xpath(cls.POLICIES):
            details = policy.xpath('following-sibling::tr')
            parent = lxml.html.HtmlElement('div')
            parent.insert(0, details[0])
            parent.insert(0, policy)
            yield parent
        for page in cls.change_page(node):
            yield page

    @classmethod
    def change_page(cls, node) -> Generator[lxml.html.HtmlElement, None, None]:
        next_link = node.xpath('//tfoot//a[contains(., "Next")]/@href')
        if len(next_link) == 0:
            return
        next_link = cls.host() + next_link[0]
        for page in cls.get_next_page(next_link):
            yield page

    @classmethod
    def get_next_page(cls, link) -> Generator[lxml.html.HtmlElement, None, None]:
        from fetchdata import FetchData
        next_page = FetchData.uri_to_xpath(link)
        cls.tree = next_page
        for policy in cls.fetch_policies(next_page, None):
            yield policy

    @classmethod
    def fetch_policies(cls, tree: lxml.html.HtmlElement, _=None) -> Generator[Policy, None, None]:
        if tree is not None:
            policies = cls.fetch_on_this_page(tree)
            for policy in policies:
                if isinstance(policy, PlaceholderPolicy):
                    yield policy
                else:
                    yield cls.fetch_policy(policy)

    @classmethod
    def fetch_policy(cls, tree: lxml.html.HtmlElement, _=None):
        return Carrier.fetch_policy(tree, PlaceholderPolicy)
