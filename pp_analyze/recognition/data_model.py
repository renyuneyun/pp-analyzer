from typing import Generic, TypeVar, Type, Optional
from pydantic import BaseModel


def to_dict(obj_or_list: list[BaseModel] | BaseModel) -> dict | list[dict]:
    if isinstance(obj_or_list, list):
        return [to_dict(x) for x in obj_or_list]
    return obj_or_list.model_dump()


class _BaseModel(BaseModel):
    class Config:
        frozen = True


T = TypeVar('T')
T2 = TypeVar('T2')
T3 = TypeVar('T3')


class WithId(_BaseModel):
    id: str


class IEntity(_BaseModel):
    text: str
    span: tuple[int, int]


class ClassifiedEntity(IEntity):
    category: str


class IPartyEntity(_BaseModel):
    text: str
    party_type: str


class SWEntities(_BaseModel, Generic[T]):
    segment: str
    entities: list[T]


IDataEntity = IEntity
IPurposeEntity = IEntity
ClassifiedDataEntity = ClassifiedEntity
ClassifiedPurposeEntity = ClassifiedEntity

SWDataEntities = SWEntities[IDataEntity]
SWClassifiedDataEntities = SWEntities[ClassifiedDataEntity]
SWPurposeEntities = SWEntities[IPurposeEntity]
SWClassifiedPurposeEntities = SWEntities[ClassifiedPurposeEntity]
SWPartyEntities = SWEntities[IPartyEntity]


class IDataPractice(_BaseModel):
    type: str
    text: str
    span: tuple[int, int]


class GenericSWDataPractices(_BaseModel, Generic[T]):
    segment: str
    practices: list[T]


SWDataPractices = GenericSWDataPractices[IDataPractice]


class GenericGroupedDataPractice(IDataPractice, Generic[T, T2, T3]):
    data: list[T]
    purpose: list[T2]
    parties: list[T3]


GroupedDataPractice = GenericGroupedDataPractice[ClassifiedDataEntity, ClassifiedPurposeEntity, IPartyEntity]
SWGroupedDataPractice = GenericSWDataPractices[GroupedDataPractice]


class ClassifiedDataEntityWithId(ClassifiedDataEntity, WithId): pass
class ClassifiedPurposeEntityWithId(ClassifiedPurposeEntity, WithId): pass
class PartyEntityWithId(IPartyEntity, WithId): pass
class GroupedDataPracticeWithId(GenericGroupedDataPractice[ClassifiedDataEntityWithId, ClassifiedPurposeEntityWithId, PartyEntityWithId], WithId): pass


SWGroupedDataPracticeWithId = GenericSWDataPractices[GroupedDataPracticeWithId]


class Relation(_BaseModel):
    action_id: str
    entity_id: str
    relation: str