from abc import ABC
from typing import Mapping, ClassVar, List, Callable, Optional, Type, Generator
from datetime import date
from decimal import Decimal

import lxml.html

from customtypes import PolicyFields, Customer, Agent, IndexedXpath


class Policy(ABC):
    """
    A policy is a datatype that is present within a carrier page.
    Each policy type should inherit this class.
    """

    # Where each part of one policy can be found from a given XPath node.
    policy_xpath: ClassVar[Mapping[PolicyFields, IndexedXpath]] = {}

    # Not all carriers use all the possible fields.
    # These are the ones the current carrier uses.
    used_fields: ClassVar[List[PolicyFields]] = []

    # The callables that will be used to convert the data to the correct type.
    # It may not be the data type itself. See for example, Carrier.us_date.
    # This should probably be renamed.
    data_types: ClassVar[Mapping[PolicyFields, Callable]] = {}

    _serialize = ['id', 'premium', 'status', 'effective_date', 'effective_date',
                  'termination_date', 'last_payment_date', 'commission_rate', 'number_of_insured']

    def to_dict(self) -> dict:
        """
        Serialize to a dictionary.
        This method should not need to be overridden.
        """
        policy_copy = self.__dict__.copy()

        for key in policy_copy.copy().keys():
            if key not in self._serialize:
                del policy_copy[key]

        policy_copy['status'] = policy_copy['status'].name

        for date_type in ['effective_date', 'termination_date', 'last_payment_date']:
            policy_copy[date_type] = policy_copy[date_type].isocalendar()

        for decimal in ['commission_rate', 'premium']:
            try:
                policy_copy[decimal] = float(policy_copy[decimal])
            except KeyError:
                pass

        return policy_copy


class Carrier(ABC):
    """
    An abstract class that all carriers will be based on.
    """

    name = "Generic carrier"

    system_name = "GENERIC_CARRIER"

    # The XPath address of each policy item.
    POLICIES: str

    # The web location of this carrier.
    URI: str

    # The policy type this carrier will return.
    policy_type: any

    # The root of the page of XPath searches.
    tree: Optional[lxml.html.HtmlElement] = None

    DateSeparators = frozenset(['-', '/'])

    @classmethod
    def us_date(cls, date_in: str) -> date:
        """
        Takes a string date in 'dd/mm/yyyy' format and converts it into a Python date.
        :param date_in: A text date in dd/mm/yyyy format.
        :return: A Python date of the same value as the text input.
        """
        # Handle one-digit month AND day:
        if date_in.startswith(':'):
            date_in = date_in[1:]

        for separator in cls.DateSeparators:
            if separator in date_in:
                parts = [int(num) for num in date_in.split(separator)]
                return date(parts[2], parts[0], parts[1])
        raise ValueError(f'Date format cannot be handled for input: "{date_in}".')

    @staticmethod
    def to_decimal(number: str) -> Decimal:
        """
        Takes a string as present in the HTML pages and converts it to a Python Decimal format.
        For financial information, neither integers nor floats are precise enough, and keeping the
        information as strings is error-pone.
        :param number: The number as a string.
        :return: The number in pythvon Decimal type.
        """
        if number.endswith('%'):
            number = number[:-1]
        number = number.split(' ')[1]
        return Decimal(number)

    @classmethod
    def fetch_policies(cls, tree: lxml.html.HtmlElement, xpath: str) -> Generator[lxml.html.HtmlElement, None, None]:
        """
        Generator for all the policies of this carrier.
        """
        for policy in tree.xpath(xpath):
            yield policy

    @classmethod
    def fetch_policy(cls, policy: lxml.html.HtmlElement, policy_type) -> Optional[Type[Policy]]:
        """
        Fetch data for a single policy and build its object.
        """
        attributes = []
        for field in policy_type.used_fields:
            xpath = policy_type.policy_xpath[field]
            data = policy.xpath(xpath.xpath)
            if not isinstance(data, str):
                data = data[xpath.place]
            data = policy_type.data_types[field](data)
            attributes.append(data)
        result = policy_type(*attributes)
        return result

    # The XPath coordinates to get the Agent information on this page.
    agent_xpath: Mapping[Agent.Fields, IndexedXpath] = {}

    # The XPath coordinates to get the Customer information on this page.
    customer_xpath: Mapping[Customer.Fields, IndexedXpath] = {}
