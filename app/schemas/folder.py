from pydantic import BaseModel


class FolderSchema(BaseModel):
    id: str
    name: str
