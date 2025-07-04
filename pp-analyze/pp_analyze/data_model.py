from enum import Enum
from pydantic import BaseModel, Field, OnErrorOmit, validator
from typing import Optional
from .hierarchy_helper import lift_data_category_to_target, lift_purpose_to_target


type uri = str


class Party(Enum):
    FIRST_PARTY = 'first_party'
    THIRD_PARTY = 'third_party'
    USER = 'user'


class DataEntity(BaseModel):
    text: str
    category: uri

    def lift(self, targets: list[str]):
        changed = False
        res = lift_data_category_to_target(self.category, targets)
        if res != self.category:
            changed = (self.category, res)
        self.category = res
        return changed


class PurposeEntity(BaseModel):
    text: str
    category: uri

    def lift(self, targets: list[str]):
        changed = None
        res = lift_purpose_to_target(self.category, targets)
        if res != self.category:
            changed = (self.category, res)
        self.category = res
        return changed


class PartyEntity(BaseModel):
    text: str
    category: Party

    @validator("category", pre=True)
    def convert_party_name(cls, v):
        if v == "Third-party-entity":
            return "third_party"
        elif v == "First-party-entity":
            return "first_party"
        elif v == "User":
            return "user"
        else:
            return v


class Location(BaseModel):
    text: str


class Duration(BaseModel):
    text: str


class SecurityThreat(BaseModel):
    text: str


class ProtectionMethod(BaseModel):
    text: str


K_DATA_PRACTICE_DATA_COLLECTION_USE = 'data_collection_use'
K_DATA_PRACTICE_DATA_SHARING_DISCLOSURE = 'data_sharing_disclosure'
K_DATA_PRACTICE_DATA_STORAGE_RETENTION = 'data_storage_retention'
K_DATA_PRACTICE_DATA_SECURITY_PROTECTION = 'data_security_protection'

DATA_PRACTICE_NAME_MAP = {
    'collection-use': K_DATA_PRACTICE_DATA_COLLECTION_USE,
    'first-party-collection-use': K_DATA_PRACTICE_DATA_COLLECTION_USE,
    'third-party-collection-use': K_DATA_PRACTICE_DATA_COLLECTION_USE,
    'third-party-sharing-disclosure': K_DATA_PRACTICE_DATA_SHARING_DISCLOSURE,
    'data-storage-retention-deletion': K_DATA_PRACTICE_DATA_STORAGE_RETENTION,
    'data-security-protection': K_DATA_PRACTICE_DATA_SECURITY_PROTECTION
}


OmittablePartyEntity = OnErrorOmit[PartyEntity]
OmittableDataEntity = OnErrorOmit[DataEntity]
OmittablePurposeEntity = OnErrorOmit[PurposeEntity]


class DataPractice(BaseModel):
    text: str

    def lift(self, targets: list[str]):
        '''
        Lift the data practices to the target categories.
        Assumes no overlap exists in the targets of different types of data practices, and thus they are passed in as a single `targets` parameter.
        '''
        changed = False
        for field in self.model_fields:
            if hasattr(self, field):
                my_field = getattr(self, field)
                if not isinstance(my_field, list):
                    my_field = [my_field]
                for field_item in my_field:
                    if hasattr(field_item, 'lift') and issubclass(field_item.__class__, BaseModel): # Only lift those that have the `lift` method
                        ichanged = field_item.lift(targets)
                        changed = changed or ichanged
        return changed


class DataCollectionUse(DataPractice):
    data_collector: list[OmittablePartyEntity] = Field(alias='Data-Collector', default=[])  # Only one; needs to validate when used
    data_provider: list[OmittablePartyEntity] = Field(alias='Data-Provider', default=[])
    data_collected: list[OmittableDataEntity] = Field(alias='Data-Collected', default=[])
    purpose: list[OmittablePurposeEntity] = Field(alias='Purpose-Argument', default=[])


class DataSharingDisclosure(DataPractice):
    data_receiver: list[OmittablePartyEntity] = Field(alias='Data-Receiver', default=[])
    data_sharer: list[OmittablePartyEntity] = Field(alias='Data-Sharer', default=[])  # Only one; needs to validate when used
    data_provider: list[OmittablePartyEntity] = Field(alias='Data-Provider', default=[])
    data_shared: list[OmittableDataEntity] = Field(alias='Data-Shared', default=[])
    purpose: list[OmittablePurposeEntity] = Field(alias='Purpose-Argument', default=[])


class DataStorageRetention(DataPractice):
    # TODO: Not implemented yet!!!
    data_holder: list[OmittablePartyEntity] = Field(alias='Data-Holder', default=[])
    data_provider: list[OmittablePartyEntity] = Field(alias='Data-Provider', default=[])
    data_retained: list[OmittableDataEntity] = Field(alias='Data-Retained', default=[])
    storage_place: list[Location] = Field(alias='Storage-Place', default=[])
    retention_period: list[Duration] = Field(alias='Retention-Period', default=[])  # Only one; needs to validate when used
    purpose: list[OmittablePurposeEntity] = Field(alias='Purpose-Argument', default=[])


class DataSecurityProtection(DataPractice):
    data_protector: list[OmittablePartyEntity] = Field(alias='Data-Protector', default=[])
    data_provider: list[OmittablePartyEntity] = Field(alias='Data-Provider', default=[])
    data_protected: list[OmittableDataEntity] = Field(alias='Data-Protected', default=[])
    protect_against: list[SecurityThreat] = Field(alias='protect-against', default=[])
    protection_method: list[ProtectionMethod] = Field(alias='method', default=[])


class SegmentedDataPractice(BaseModel):
    '''
    A segment of the privacy policy with the relevant data practices (which are subclasses of `DataPractice`).
    '''
    class Config:
        frozenset = True

    segment: str
    practices: list[DataPractice]

    def lift(self, targets: list[str]):
        '''
        Lift the data practices to the target categories.
        Assumes no overlap exists in the targets of different types of data practices, and thus they are passed in as a single `targets` parameter.
        '''
        changed = False
        for practice in self.practices:
            ichanged = practice.lift(targets)
            changed = changed or ichanged
        return changed


DATA_PRACTICE_CLASS_MAP = {
    K_DATA_PRACTICE_DATA_COLLECTION_USE: DataCollectionUse,
    K_DATA_PRACTICE_DATA_SHARING_DISCLOSURE: DataSharingDisclosure,
    K_DATA_PRACTICE_DATA_STORAGE_RETENTION: DataStorageRetention,
    K_DATA_PRACTICE_DATA_SECURITY_PROTECTION: DataSecurityProtection,
}
