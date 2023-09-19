from pydantic import BaseModel, Field


class ScopeUserSchema(BaseModel):
    id: str


class UserCreateSchema(BaseModel):
    id: str = Field(alias="chat_id")
