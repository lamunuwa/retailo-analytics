from pydantic import BaseModel, ConfigDict


class StoreCreate(BaseModel):
    name: str


class StoreResponse(StoreCreate):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
