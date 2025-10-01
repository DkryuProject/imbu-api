from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class IncludedVersion(BaseModel):
    id: str
    name: str
    displayName: str
    createTime: str
    lastModifiedTime: str
    fileType: str
    versionNumber: int
    derivativesId: Optional[str]

    @classmethod
    def from_json(cls, item: Dict[str, Any]) -> "IncludedVersion":
        attrs = item.get("attributes", {})
        derivatives = item.get("relationships", {}).get("derivatives", {})
        derivatives_id = None

        if derivatives and isinstance(derivatives, dict):
            data = derivatives.get("data")
            if data and isinstance(data, dict):
                derivatives_id = data.get("id")

        return cls(
            id=item.get("id"),
            name=attrs.get("name"),
            displayName=attrs.get("displayName"),
            createTime=attrs.get("createTime"),
            lastModifiedTime=attrs.get("lastModifiedTime"),
            fileType=attrs.get("fileType"),
            versionNumber=attrs.get("versionNumber", 0),
            derivativesId=derivatives_id
        )


# included 전체 처리: versionNumber 기준 가장 큰 것 반환
def get_latest_version(included: List[Dict[str, Any]]) -> Optional[IncludedVersion]:
    versions = [IncludedVersion.from_json(item) for item in included]
    if not versions:
        return None
    return max(versions, key=lambda x: x.versionNumber)
