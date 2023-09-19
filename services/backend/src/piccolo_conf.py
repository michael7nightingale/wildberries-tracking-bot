from piccolo.conf.apps import AppRegistry
from piccolo.engine import SQLiteEngine, PostgresEngine


APP_REGISTRY = AppRegistry(
    apps=["db.piccolo_app"]
)

from db.config import DB

