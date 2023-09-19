from pydantic import BaseModel


class ParsingCreateSchema(BaseModel):
    article: str
    title: str
