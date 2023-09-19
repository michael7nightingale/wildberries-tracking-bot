from piccolo.table import Table
from piccolo.columns import Varchar

from .config import DB


class User(Table, db=DB):
    id = Varchar(primary_key=True, index=True, unique=True)


table_list = [User]
