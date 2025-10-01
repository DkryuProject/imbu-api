from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union
from datetime import datetime
from dateutil.parser import parse


class ElementPropertyModel(BaseModel):
    property_name: str = Field(..., alias="name")
    property_value: Optional[Union[str, float, bool]] = Field(None, alias="value")

    model_config = {
        "populate_by_name": True
    }


class ElementModel(BaseModel):
    element_id: str
    name: str
    type: str
    base_constraint: str
    top_constraint: str
    category: str
    family_name: str
    element_name: str
    revit_element_id: str
    created_on: Optional[datetime] = Field(None, alias="createdOn")
    last_modified_on: Optional[datetime] = Field(None, alias="lastModifiedOn")
    properties: List[ElementPropertyModel]

    # Pydantic v2 style validator
    @field_validator("created_on", "last_modified_on", mode="before")
    @classmethod
    def parse_datetime(cls, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        return parse(value)  # dateutil.parser 사용

    model_config = {
        "populate_by_name": True
    }


class CategoryRequest(BaseModel):
    group_id: str
    category: str
