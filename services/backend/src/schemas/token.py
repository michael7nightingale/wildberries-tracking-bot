from pydantic import BaseModel
from datetime import datetime


class Token(BaseModel):
    exp: datetime
    id: str
