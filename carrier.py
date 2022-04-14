from abc import ABC, abstractmethod
from typing import Mapping, ClassVar, List, Callable, Optional
from datetime import date

import lxml.html

from customtypes import PolicyFields, Customer, Agent, IndexedXpath


class Carrier(ABC):
    """
    An abstract class that all carriers will be based on.
    """

    # The root of the page of XPath searches.
    tree: lxml.html.HtmlElement

    # The XPath address of each policy item.
    POLICIES: str

    # The web location of this carrier.
    URI: str

    # The policy type this carrier will return.
    policy_type: any

    tree: Optional[lxml.html.HtmlElement] = None

    DateSeparators = frozenset(['-', '/'])

    @classmethod
    def us_date(cls, date_in: str, reverse=True) -> date:
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
    def to_decimal(number: str):
        from decimal import Decimal
        if number.endswith('%'):
            number = number[:-1]
        number = number.split(' ')[1]
        return Decimal(number)

    class Policy:
        """
        Information and details about a single policy.
        """

    @classmethod
    def fetch_policies(cls, tree: lxml.html.HtmlElement, xpath: str):
        """
        Generator for all the policies of this carrier.
        """
        for policy in tree.xpath(xpath):
            yield policy

    @classmethod
    def fetch_policy(cls, policy_type, policy: lxml.html.HtmlElement):
        """
        Fetch data for a single policy and build its object.
        """
        if policy is None or policy_type is Carrier.Policy:
            return
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
    agents_xpath: Mapping[Agent.Fields, IndexedXpath] = {}

    # The XPath coordinates to get the Customer information on this page.
    customer_xpath: Mapping[Customer.Fields, IndexedXpath] = {}


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
