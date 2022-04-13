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
        PolicyFields.Status: Status,
        PolicyFields.EffectiveDate: Carrier.us_date,
        PolicyFields.TerminationDate: Carrier.us_date,
        PolicyFields.LastPaymentDate: Carrier.us_date
    }

    policy_xpath: ClassVar[Mapping[PolicyFields, IndexedXpath]] = {
        PolicyFields.Id: IndexedXpath('//div[@for="id"]', 0),
        PolicyFields.Premium: IndexedXpath('//div[@for="premium"]', 0),
        PolicyFields.Status: IndexedXpath('//div[@for="status"]', 0),
        PolicyFields.EffectiveDate: IndexedXpath('//div[@for="effectiveDate"]', 0),
        PolicyFields.TerminationDate: IndexedXpath('//div[@for="terminationDate"]', 0),
        PolicyFields.LastPaymentDate: IndexedXpath('//div[@for="lastPaymentDate"]', 0),
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

    POLICIES = '//tr[contains(@class, "policy-info-row")]'

    agents_xpath: Mapping[Agent.Fields, IndexedXpath] = {
        Agent.Fields.Name:
            IndexedXpath('//dd[@class="value-name value-holder"][@data-value-for="name"]/text()', 0),
        Agent.Fields.ProducerCode:
            IndexedXpath('//dd[@class="value-producerCode value-holder"][@data-value-for="producerCode"]/text()', 0),
        Agent.Fields.AgencyName:
            IndexedXpath('//dd[@class="value-agencyName value-holder"][@data-value-for="agencyName"]/text()', 0),
        Agent.Fields.AgencyCode:
            IndexedXpath('//dd[@class="value-agencyCode value-holder"][@data-value-for="agencyCode"]/text()', 0),
    }

    customer_xpath: Mapping[Customer.Fields, IndexedXpath] = {
        Customer.Fields.Name:
            IndexedXpath('//dd [@class="value-name value-holder"][@data-value-for="name"]/text()', 1),
        Customer.Fields.Id:
            IndexedXpath('//dd [@class="value-id value-holder"][@data-value-for="id"]/text()', 0),
        Customer.Fields.Email:
            IndexedXpath('//dd [@class="value-email value-holder"][@data-value-for="email"]/text()', 0),
        Customer.Fields.Address:
            IndexedXpath('//dd [@class="value-address value-holder"][@data-value-for="address"]/text()', 0)
    }
