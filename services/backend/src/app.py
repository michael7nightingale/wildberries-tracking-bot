from litestar import Litestar
from litestar.middleware import DefineMiddleware

from internal.routes import router
from internal.auth import AuthenticationMiddleware


def create_app() -> Litestar:
    app = Litestar(
        route_handlers=[router],
        middleware=[DefineMiddleware(AuthenticationMiddleware)],

    )
    return app
