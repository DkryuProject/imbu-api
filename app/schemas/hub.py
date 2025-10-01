from pydantic import BaseModel


class HubSchema(BaseModel):
    id: str
    name: str
