from collections import defaultdict
from pydantic import BaseModel
from rdflib import IdentifiedNode, Graph, URIRef, BNode, Namespace, Literal
from .data_model import (
    SegmentedDataPractice,
    DataCollectionUse,
    DataSharingDisclosure,
    DataStorageRetention,
    DataSecurityProtection,
    Party,
)
from .kg import convert_to_kg, one, A, NS, NS_DPV


NS_DTOU = Namespace("urn:dtou:core#")
NS_EX = Namespace("http://example.org/ns#")


class Downstream(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    text: str
    user: str | None = None
    app_name: str | None = None
    purpose: list[IdentifiedNode] = []
    # security: list[str] = []


class InputSpec(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    text: str
    data: IdentifiedNode
    user: str | None = None
    action: str | None = None
    purpose: list[IdentifiedNode] = []
    # security: list[str] = []
    downstream: list[Downstream] = []


class AppPolicy(BaseModel):
    '''
    Specialized AppPolicy for PoliAnalyzer.
    It resemble the AppPolicy in Perennial DToU policy language, but uses specialized fields in Python class.
    '''
    app_name: str
    input_spec: list[InputSpec] = []

    def to_rdf(self):
        '''
        Convert the AppPolicy to RDF app policy document.
        '''
        g = Graph()
        g.bind('dtou', NS_DTOU)
        g.bind('dpv', NS_DPV)
        g.bind('ex', NS_EX)
        n_policy = NS_EX['policy1']
        g.add((n_policy, A, NS_DTOU['AppPolicy']))
        g.add((n_policy, NS_DTOU['app_name'], URIRef(self.app_name)))
        for i, input_spec in enumerate(self.input_spec):
            n_input_spec = BNode()
            g.add((n_policy, NS_DTOU['input_spec'], n_input_spec))
            g.add((n_input_spec, A, NS_DTOU['InputSpec']))
            g.add((n_input_spec, NS['text'], Literal(input_spec.text)))

            port_name = f"inputPort{i}"
            n_port = BNode()
            g.add((n_input_spec, NS_DTOU['port'], n_port))
            g.add((n_port, A, NS_DTOU['Port']))
            g.add((n_port, NS_DTOU['name'], Literal(port_name)))

            g.add((n_input_spec, NS_DTOU['data'], input_spec.data))
            if input_spec.user:
                g.add((n_input_spec, NS_DTOU['user'], Literal(input_spec.user)))
            if input_spec.action:
                g.add((n_input_spec, NS_DTOU['action'], Literal(input_spec.action)))
            for purpose in input_spec.purpose:
                n_pe = BNode()
                g.add((n_input_spec, NS_DTOU['purpose'], n_pe))
                g.add((n_pe, A, NS_DTOU['Expectation']))
                g.add((n_pe, NS_DTOU['category'], NS_DTOU['PurposeCategory']))
                g.add((n_pe, NS_DTOU['descriptor'], purpose))
            for downstream in input_spec.downstream:
                n_downstream = BNode()
                g.add((n_input_spec, NS_DTOU['downstream'], n_downstream))
                g.add((n_downstream, NS['text'], Literal(downstream.text)))
                if downstream.user:
                    g.add((n_downstream, NS_DTOU['user'], Literal(downstream.user)))
                if downstream.app_name:
                    g.add((n_downstream, NS_DTOU['app_name'], Literal(downstream.app_name)))
                for purpose in downstream.purpose:
                    n_pe = BNode()
                    g.add((n_input_spec, NS_DTOU['purpose'], n_pe))
                    g.add((n_pe, A, NS_DPV['Expectation']))
                    g.add((n_pe, NS_DTOU['category'], NS_DTOU['PurposeCategory']))
                    g.add((n_pe, NS_DTOU['descriptor'], purpose))
        return g


def convert_to_app_policy(data_practices: list[SegmentedDataPractice], app_name: str, first_party: str) -> AppPolicy:
    """
    Convert the data practices to *app policy* as in Perennial DToU policy language.
    Assume the passed in data_practices belong to the same privacy policy, e.g. output from `pp_analyze.analyze_pp`.
    """
    kg = convert_to_kg(data_practices, app_name, first_party)

    app_policy = AppPolicy(app_name=app_name)

    n_pp = one(kg.subjects(A, NS['PrivacyPolicy']))

    def to_user_field(party: IdentifiedNode) -> str:
        if (party, A, NS['FirstParty']) in kg:
            return first_party
        elif (party, A, NS['ThirdParty']) in kg:
            return one(kg.objects(party, NS['name'])).toPython()
        else:
            raise ValueError("`User` should not appear in this context")

    def construct_downstream_from_data_sharing(n_practice):
        ds_text = kg.value(kg.value(n_practice, NS['text']), NS['value']).toPython()
        receiver_list = [o for o in kg.objects(n_practice, NS['receiver'])]
        purpose_list = [o for o in kg.objects(n_practice, NS['purpose'])]
        if not receiver_list:
            return [Downstream(
                text=ds_text,
                user=None,
                purpose=purpose_list
            )]
        else:
            return [Downstream(
                        text=ds_text,
                        user=to_user_field(user),
                        purpose=purpose_list
                    ) for user in receiver_list]


    for n_practice in kg.objects(n_pp, NS['hasDataPractice']):
        if (n_practice, A, NS['DataCollectionUse']) not in kg:
            continue
        text = kg.value(kg.value(n_practice, NS['text']), NS['value']).toPython()
        data_list = [o for o in kg.objects(n_practice, NS['data'])]
        purpose_list = [o for o in kg.objects(n_practice, NS['purpose'])]
        user_list = [o for o in kg.objects(n_practice, NS['user'])]
        for data in data_list:
            # assert not user_list or len(user_list) == 1
            user = user_list[0] if user_list else None
            downstreams = []
            downstream_nodes = []
            for n_practice_share in kg.subjects(A, NS['DataSharingDisclosure']):
                if (n_pp, NS['hasDataPractice'], n_practice_share) not in kg:
                    continue
                if (n_practice_share, NS['data'], data) not in kg:
                    continue
                downstream_nodes.append(n_practice_share)
                downstreams.extend(construct_downstream_from_data_sharing(n_practice_share))

            input_spec = InputSpec(
                data=data,
                text=text,
                user=to_user_field(user),
                purpose=purpose_list,
                downstream=downstreams
            )
            app_policy.input_spec.append(input_spec)

    for n_practice in kg.objects(n_pp, NS['hasDataPractice']):
        if (n_practice, A, NS['DataSharingDisclosure']) not in kg:
            continue
        text = kg.value(kg.value(n_practice, NS['text']), NS['value']).toPython()
        data_list = [o for o in kg.objects(n_practice, NS['data'])]
        for data in data_list:
            has_first_party_use = False
            for n_practice2 in kg.subjects(NS['data'], data):
                if (n_pp, NS['hasDataPractice'], n_practice2) not in kg:
                    continue
                if (n_practice2, A, NS['DataCollectionUse']) in kg:
                    has_first_party_use = True
                    break
            if has_first_party_use:
                continue
            downstreams = construct_downstream_from_data_sharing(n_practice)
            input_spec = InputSpec(
                text=text,
                data=data,
                downstream=downstreams
            )
            app_policy.input_spec.append(input_spec)

    return app_policy