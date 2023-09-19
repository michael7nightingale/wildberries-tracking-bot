import os
from piccolo.conf.apps import AppConfig

from .tables import table_list


CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

APP_CONFIG = AppConfig(
    app_name='db',
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, 'migrations'),
    table_classes=table_list,
    migration_dependencies=[],
    commands=[]
)
