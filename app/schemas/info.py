from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class InfoRequest(BaseModel):
    urn: str
    dbId: int


class MetadataItem(BaseModel):
    name: str
    role: str
    guid: str


class MetadataData(BaseModel):
    type: str
    metadata: List[MetadataItem]


class MetadataResponse(BaseModel):
    data: MetadataData


class ElementId(BaseModel):
    Value: str


class PropertyCollection(BaseModel):
    objectid: int
    name: str
    externalId: str
    properties: Dict[str, Any]  # 전체 속성은 동적이라 Dict로 둠


class PropertiesData(BaseModel):
    type: str
    collection: List[PropertyCollection]


class PropertiesResponse(BaseModel):
    data: PropertiesData
