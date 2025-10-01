from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator


class ProjectSchema(BaseModel):
    id: str
    name: str
    data_management_api_project_id: Optional[str] = Field(
        None, alias="dataManagementAPIProjectId"
    )

    # Pydantic v2: 모델 검증기
    @model_validator(mode='before')
    def extract_alternative_identifiers(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        API 응답이 alternativeIdentifiers 안에 dataManagementAPIProjectId를 담고 있을 때
        이를 flatten해서 data_management_api_project_id 필드로 이동
        """
        alt = values.get("alternativeIdentifiers") or {}
        dm_id = alt.get("dataManagementAPIProjectId")
        if dm_id:
            values["data_management_api_project_id"] = dm_id
            values["dataManagementAPIProjectId"] = dm_id
        return values

    model_config = {
        "populate_by_name": True,  # v1의 allow_population_by_field_name
        "validate_assignment": True
    }
