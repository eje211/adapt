"""
All the custom types that this script uses.
"""

from dataclasses import dataclass
from typing import ClassVar, Mapping, Optional, Callable, List
from collections import namedtuple
from enum import Enum, auto

# An XPath reference and index of which item will be returned if more than one
# result is expected.
IndexedXpath = namedtuple('IndexedXpath', ['xpath', 'place'])


@dataclass
class Agent:
    """
    The costumer's agent details.
    """
    name: str
    producer_code: str
    agency_name: str
    agency_code: str

    class Fields(Enum):
        Name = auto()
        ProducerCode = auto()
        AgencyName = auto()
        AgencyCode = auto()

    types: ClassVar[Mapping[Fields, str]] = {
        Fields.Name: str,
        Fields.ProducerCode: str,
        Fields.AgencyName: str,
        Fields.AgencyCode: str
    }

    _serialize = ['name', 'producer_code', 'agency_name', 'agency_code']

    def to_dict(self) -> dict:
        """
        Serialize to a dictionary.
        """
        agent_copy = self.__dict__.copy()
        for key in agent_copy.copy().keys():
            if key not in self._serialize:
                del agent_copy[key]
        return agent_copy


@dataclass
class Customer:
    """
    Identity and information about the customer.
    Which user data is used can vary from one carrier to the next.
    """
    name: str
    id: str
    email: str
    address: str
    ssn: Optional[int] = None
    agent: Optional[Agent] = None
    policies: Optional[List] = None

    class Fields(Enum):
        Name = auto()
        Id = auto()
        Email = auto()
        Address = auto()
        SSN = auto()

    types: ClassVar[Mapping[Fields, Callable]] = {
        Fields.Name: str,
        Fields.Id: str,
        Fields.Email: str,
        Fields.Address: str,
        Fields.SSN: int,
    }

    _serialize = ['name', 'id', 'email', 'address', 'ssn', 'agent', 'policies']

    def to_dict(self) -> dict:
        """
        Serialize to a dictionary.
        """
        customer_copy = self.__dict__.copy()
        for key in customer_copy.copy().keys():
            if key not in self._serialize:
                del customer_copy[key]
        customer_copy['agent'] = customer_copy['agent'].to_dict()
        customer_copy['policies'] = {key: policy.to_dict() for key, policy in customer_copy['policies'].items()}
        return customer_copy


class PolicyFields(Enum):
    """
    Not all of the policy fields are used in all of the policies.
    """
    Id = auto()
    Premium = auto()
    Status = auto()
    EffectiveDate = auto()
    TerminationDate = auto()
    LastPaymentDate = auto()
    CommissionRate = auto()
    NumberOfInsured = auto()


class Status(Enum):
    """
    The possible states a policy can be in.
    This can naturally be updated as needed.
    Static methods can be added for more flexible input values.
    If the data from the pages is not reliable, this enum cad be set using fuzzy text.
    """
    active = auto()
    endorsement_pending = auto()
    pending_cancelation = auto()  # This is how it is spelt in the documents.
    claim_pending = auto()
    claim_rejected = auto()
