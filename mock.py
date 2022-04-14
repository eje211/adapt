import lxml.html
from carrier import Carrier, Policy
from decimal import *
from customtypes import PolicyFields, Status, Agent, Customer, IndexedXpath
from typing import ClassVar, Mapping, List, Optional, Callable
from datetime import date
from dataclasses import dataclass


@dataclass
class MockPolicy(Policy):
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

    used_fields: ClassVar[List[PolicyFields]] = [
        PolicyFields.Id, PolicyFields.Premium, PolicyFields.Status,
        PolicyFields.EffectiveDate, PolicyFields.TerminationDate,
        PolicyFields.LastPaymentDate
    ]

    data_types: ClassVar[Mapping[PolicyFields, Callable]] = {
        PolicyFields.Id: str,
        PolicyFields.Premium: Decimal,
        PolicyFields.Status: Status.__getitem__,
        PolicyFields.EffectiveDate: Carrier.us_date,
        PolicyFields.TerminationDate: Carrier.us_date,
        PolicyFields.LastPaymentDate: Carrier.us_date
    }

    policy_xpath: ClassVar[Mapping[PolicyFields, IndexedXpath]] = {
        PolicyFields.Id:
            IndexedXpath('//label[@for="id"]/following-sibling::span/text()', 0),
        PolicyFields.Premium:
            IndexedXpath('//label[@for="premium"]/following-sibling::span/text()', 0),
        PolicyFields.Status:
            IndexedXpath('//label[@for="status"]/following-sibling::span/text()', 0),
        PolicyFields.EffectiveDate:
            IndexedXpath('//label[@for="effectiveDate"]/following-sibling::span/text()', 0),
        PolicyFields.TerminationDate:
            IndexedXpath('//label[@for="terminationDate"]/following-sibling::span/text()', 0),
        PolicyFields.LastPaymentDate:
            IndexedXpath('//label[@for="lastPaymentDate"]/following-sibling::span/text()', 0),
    }


class Mock(Carrier):
    """
    The implementation of the Mock Indemnity carrier.
    This carrier uses simple pages with no frames, no JavaScript.
    Every policy is one a single page for one client.
    """

    def __init__(self):
        self.policy_elements: Mapping[int, lxml.html.HtmlElement] = {}

    policy_type = MockPolicy

    tree: Optional[lxml.html.HtmlElement] = None

    URI = 'https://scraping-interview.onrender.com/mock_indemnity/a0dfjw9a'

    POLICIES = '//li[@class="list-group-item"]'

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

    customer_xpath: Mapping[Customer.Fields, IndexedXpath] = {
        Customer.Fields.Name:
            IndexedXpath('//dd[@class="value-name value-holder"][@data-value-for="name"]/text()', 1),
        Customer.Fields.Id:
            IndexedXpath('//dd[@class="value-id value-holder"][@data-value-for="id"]/text()', 0),
        Customer.Fields.Email:
            IndexedXpath('//dd[@class="value-email value-holder"][@data-value-for="email"]/text()', 0),
        Customer.Fields.Address:
            IndexedXpath('//dd[@class="value-address value-holder"][@data-value-for="address"]/text()', 0)
    }

    @classmethod
    def fetch_policy(cls,  _, policy: lxml.html.HtmlElement):
        return super().fetch_policy(MockPolicy, policy)

    @classmethod
    def fetch_policies(cls, tree: lxml.html.HtmlElement, policies: List[str]):
        return Carrier.fetch_policies(cls.tree, cls.POLICIES)
