from litestar.middleware.authentication import AbstractAuthenticationMiddleware, AuthenticationResult
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException

from datetime import datetime, timedelta
from jose import jwt, JWTError

from db.services import get_user
from settings import get_settings
from schemas.users import ScopeUserSchema
from schemas.token import Token


def decode_token(encoded_token: str, settings=get_settings()) -> Token | None:
    try:
        decoded_data = jwt.decode(
            token=encoded_token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if 'id' in decoded_data:
            decoded_data['id'] = str(decoded_data['id'])
        return Token(**decoded_data)
    except JWTError:
        return


def encode_token(chat_id: str, settings=get_settings()) -> str:
    token_data = {
        'exp': datetime.now() + timedelta(minutes=settings.EXPIRE_MINUTES),
        'id': chat_id
    }
    return jwt.encode(
        claims=token_data,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


class AuthenticationMiddleware(AbstractAuthenticationMiddleware):

    async def authenticate_request(self, connection: ASGIConnection) -> AuthenticationResult:
        token = connection.headers.get("token")
        if token is None or token != get_settings().TELEGRAM_CONTEXT_KEY:
            raise NotAuthorizedException(detail="Authentication token required.")

        authentication_jwt_token = connection.headers.get("authorization")
        if authentication_jwt_token is not None:
            token_data = decode_token(authentication_jwt_token)
            if token_data is not None:
                user = await get_user(token_data.id)
                if user is not None:
                    return AuthenticationResult(ScopeUserSchema(**user), authentication_jwt_token)

        return AuthenticationResult(None, None)
