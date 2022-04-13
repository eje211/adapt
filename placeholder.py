from carrier import Carrier, Policy
from decimal import *
from customtypes import PolicyFields, Status, Agent, Customer, IndexedXpath
from typing import ClassVar, Mapping, List, Callable
from datetime import date
import lxml.html
from dataclasses import dataclass


class Placeholder(Carrier):
    """
    The implementation of the Placeholder Carrier.
    This carrier uses simple pages with no frames, no JavaScript.
    Every policy is one its own page for each client.
    """

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

        _fields: ClassVar[List[PolicyFields]] = [
            PolicyFields.Id, PolicyFields.Premium, PolicyFields.Status,
            PolicyFields.EffectiveDate, PolicyFields.TerminationDate,
            PolicyFields.LastPaymentDate, PolicyFields.CommissionRate,
            PolicyFields.NumberOfInsured
        ]

        data_types: ClassVar[Mapping[PolicyFields, Callable]] = {
            PolicyFields.Id: str,
            PolicyFields.Premium: Decimal,
            PolicyFields.Status: Status,
            PolicyFields.EffectiveDate: Carrier.us_date,
            PolicyFields.TerminationDate: Carrier.us_date,
            PolicyFields.LastPaymentDate: Carrier.us_date,
            PolicyFields.CommissionRate: Decimal,
            PolicyFields.NumberOfInsured: int
        }

        agents_xpath: ClassVar[Mapping[Agent.Fields, IndexedXpath]] = {
            PolicyFields.Id: IndexedXpath('id', 0),
            PolicyFields.Premium: IndexedXpath('premium', 0),
            PolicyFields.Status: IndexedXpath('status', 0),
            PolicyFields.EffectiveDate: IndexedXpath('effective_date', 0),
            PolicyFields.TerminationDate: IndexedXpath('termination_date', 0),
            PolicyFields.LastPaymentDate: IndexedXpath('last_payment_date', 0),
            PolicyFields.CommissionRate: IndexedXpath('termination_date', 0),
            PolicyFields.NumberOfInsured: IndexedXpath('last_payment_date', 0),
        }

    URI = 'https://scraping-interview.onrender.com/placeholder_carrier/f02dkl4e/policies/1'

    agents_xpath: Mapping[Agent.Fields, IndexedXpath] = {
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

    def fetch_policies(self):
        yield self.fetch_on_this_page(self.tree)

    def fetch_on_this_page(self, node):
        for policy in self.tree.xpath(self.POLICIES):
            yield self.fetch_policy(policy)
        next_link = self.tree.xpath('//tfoot//a[contains(., "Next")]/@href')
        if len(next_link) == 0:
            return
        next_link = next_link[0].split('=')[1][1:-1]
        yield self.get_next_page(next_link)

    def get_next_page(self, link):
        from fetchdata import FetchData
        next_page = FetchData.uri_to_xpath(link)
        yield self.fetch_on_this_page(next_page)
