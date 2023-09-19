from litestar import post, Request, Router
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.enums import RequestEncodingType

from typing import Annotated

from schemas.parsing import ParsingCreateSchema
from schemas.users import UserCreateSchema
from db.services import create_user
from worker import parsing_task


@post("/users", status_code=201)
async def user_create(
        request: Request,
        data: Annotated[UserCreateSchema, Body(content_encoding=RequestEncodingType.JSON)]
) -> dict:
    new_user_data = await create_user(**data.dict())
    if new_user_data is None:
        raise HTTPException(detail="Chat already exists.", status_code=400)
    return new_user_data


@post("/parsing")
async def parsing_create(
        request: Request,
        data: Annotated[ParsingCreateSchema, Body(content_encoding=RequestEncodingType.JSON)]
) -> None:
    parsing_task.apply_async(args=[data.title, data.article, request.user.id])


router = Router(route_handlers=[user_create, parsing_create], path="/api/v1")
