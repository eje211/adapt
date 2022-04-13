from abc import ABC, abstractmethod
from typing import Mapping, ClassVar, List, Callable
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

    @staticmethod
    def us_date(date_in) -> date:
        """
        Takes a string date in 'dd/mm/yyyy' format and converts it into a Python date.
        :param date_in: A text date in dd/mm/yyyy format.
        :return: A Python date of the same value as the text input.
        """
        parts = [int(num) for num in date_in.split('/')]
        parts.reverse()
        return date(*parts)

    class Policy:
        """
        Information and details about a single policy.
        """

    def fetch_policies(self):
        """
        Generator for all the policies of this carrier.
        """
        for policy in self.tree.xpath(self.POLICIES):
            yield policy

    def fetch_policy(self, policy: lxml.html.HtmlElement):
        """
        Fetch data for a single policy.
        """
        attributes = []
        for field in self.policy_type.used_fields:
            xpath = self.policy_type.policy_xpath[field]
            data = policy.xpath(xpath.xpath)[xpath.index]
            data = self.policy_type.data_types[field](data)
            attributes.append(data)
        return self.policy_type(*attributes)

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
