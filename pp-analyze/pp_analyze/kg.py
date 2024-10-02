from rdflib import Graph, Literal, Namespace, URIRef, BNode
from rdflib.namespace import RDF
from .data_model import (
    SegmentedDataPractice,
    DataCollectionUse,
    DataSharingDisclosure,
    DataStorageRetention,
    DataSecurityProtection,
    Party,
    PartyEntity,
    DataEntity,
    PurposeEntity,
    ProtectionMethod,
    SecurityThreat,
)


NS = Namespace("urn:pp-analyze:core#")
NS_DPV = Namespace("https://w3id.org/dpv#")
A = RDF.type

N_DATA_GENERAL = NS_DPV["Data-general"]
ENTITY_MAP = {
    'Data': 'Data-general',
    'Purpose-general': 'Purpose',
}


def one(iter):
    return next(iter)


def to_data_category_uri(data_category: str) -> URIRef:
    if data_category in ENTITY_MAP:
        data_category = ENTITY_MAP[data_category]
    return NS_DPV[data_category]


def to_purpose_category_uri(purpose_category: str) -> URIRef:
    if purpose_category in ENTITY_MAP:
        purpose_category = ENTITY_MAP[purpose_category]
    return NS_DPV[purpose_category]


def to_threat_uri(threat: SecurityThreat) -> URIRef:
    return NS[threat.text]


def to_protection_method_uri(protection_method: ProtectionMethod) -> URIRef:
    return NS[protection_method.text]


def convert_to_kg(data_practices: list[SegmentedDataPractice], app_name: str, first_party: str) -> Graph:
    f'''
    Convert the data practices to knowledge graph representation.
    Assume the passed in data_practices belong to the same privacy policy, e.g. output from `pp_analyze.analyze_pp`.
    Result knowledge graph will always have the following node:
    (?p a {NS["PrivacyPolicy"]})
    '''
    g = Graph()
    n_first_party = None
    n_user = None
    n_data_general = None
    def get_data_general():
        nonlocal n_data_general
        global N_DATA_GENERAL
        if n_data_general is None:
            n_data_general = N_DATA_GENERAL
            g.add((n_data_general, A, NS_DPV["Data"]))
        return n_data_general
    def to_party_uri(party: PartyEntity) -> URIRef:
        nonlocal n_first_party, n_user
        if party.category == Party.FIRST_PARTY:
            if n_first_party is None:
                n_first_party = BNode()
                g.add((n_first_party, A, NS["FirstParty"]))
                g.add((n_first_party, NS["name"], Literal(first_party)))
            party_node = n_first_party
            return party_node
        elif party.category == Party.THIRD_PARTY:
            party_node = BNode()
            g.add((party_node, A, NS["ThirdParty"]))
            g.add((party_node, NS["name"], Literal(party.text)))
            return party_node
        elif party.category == Party.USER:
            if n_user is None:
                n_user = BNode()
                g.add((n_user, A, NS["User"]))
            party_node = n_user
            return party_node
        else:
            raise ValueError(f"Unknown party type: {party}")
    def data_uri(data: DataEntity) -> URIRef:
        n_data = to_data_category_uri(data.category)
        g.add((n_data, A, NS["Data"]))
        return n_data
    def purpose_uri(purpose: PurposeEntity) -> URIRef:
        n_purpose = to_purpose_category_uri(purpose.category)
        g.add((n_purpose, A, NS["Purpose"]))
        return n_purpose
    n_site = BNode()
    g.add((n_site, A, NS['PrivacyPolicy']))
    for data_practice in data_practices:
        for practice in data_practice.practices:
            n_practice = BNode()
            g.add((n_site, NS['hasDataPractice'], n_practice))
            g.add((n_practice, A, NS[practice.__class__.__name__]))
            if isinstance(practice, DataCollectionUse):
                for party in practice.data_collector:
                    g.add((n_practice, NS["user"], to_party_uri(party)))
                for data in practice.data_collected:
                    g.add((n_practice, NS['data'], data_uri(data)))
                for purpose in practice.purpose:
                    g.add((n_practice, NS['purpose'], purpose_uri(purpose)))
                for provider in practice.data_provider:
                    g.add((n_practice, NS['provider'], to_party_uri(provider)))

                # If no data collected, but data collector and purpose are present, then assume general data
                if not practice.data_collected and practice.data_collector and practice.purpose:
                    g.add((n_practice, NS['data'], get_data_general()))
            elif isinstance(practice, DataSharingDisclosure):
                for party in practice.data_sharer:
                    g.add((n_practice, NS["sharer"], to_party_uri(party)))
                for data in practice.data_shared:
                    g.add((n_practice, NS['data'], data_uri(data)))
                for purpose in practice.purpose:
                    g.add((n_practice, NS['purpose'], purpose_uri(purpose)))
                for receiver in practice.data_receiver:
                    g.add((n_practice, NS['receiver'], to_party_uri(receiver)))
                for provider in practice.data_provider:
                    g.add((n_practice, NS['provider'], to_party_uri(provider)))

                # If no data shared, but data purpose are present, then assume general data
                if not practice.data_shared and practice.purpose:
                    g.add((n_practice, NS['data'], get_data_general()))
            elif isinstance(practice, DataStorageRetention):
                pass
            elif isinstance(practice, DataSecurityProtection):
                for party in practice.data_protector:
                    g.add((n_practice, NS["user"], to_party_uri(party)))
                for data in practice.data_protected:
                    g.add((n_practice, NS['data'], data_uri(data)))
                for provider in practice.data_provider:
                    g.add((n_practice, NS['provider'], to_party_uri(provider)))
                for threat in practice.protect_against:
                    g.add((n_practice, NS['protectAgainst'],to_threat_uri(threat)))
                for method in practice.protection_method:
                    g.add((n_practice, NS['method'], to_protection_method_uri(method)))

    return g
