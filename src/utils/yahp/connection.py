from django.conf import settings
from django.db import connections

import sqlalchemy as sa
from sqlalchemy.engine.base import Engine
from urllib.parse import quote_plus


def get_pssql_sqlalchemy_engine(connection: str = "default", database: str = None) -> Engine:
    """Get SqlAlchemy Engine

    Parameters
    ----------
    connection : str, optional
        Django Configured Connection, currently "default" or "yadc", by default "default"
    database : str, optional
        Database name else default to Django configured database name, by default None

    Returns
    -------
    Engine
        SqlAlchemy Engine
    """
    db_params = connections[connection].settings_dict

    database = database or db_params["NAME"]
    user = db_params["USER"]
    password = db_params["PASSWORD"]
    host = db_params["HOST"]
    port = db_params["PORT"]

    # Engine String
    engine_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return sa.create_engine(engine_url)


def get_mssql_sqlalchemy_engine(db: str = settings.DB_AGTECH_DB) -> Engine:
    """Get SqlAlchemy Engine

    Parameters
    ----------
    connection : str, optional
        Django Configured Connection, currently "default" or "yadc", by default "default"
    database : str, optional
        Database name else default to Django configured database name, by default None

    Returns
    -------
    Engine
        SqlAlchemy Engine
    """

    user = settings.DB_AGTECH_USER
    password = settings.DB_AGTECH_PW
    host = settings.DB_AGTECH_HOST

    # Engine String
    params = f"DRIVER={{{settings.MSSQL_DRIVER}}};SERVER={host};database={db};\
    TrustServerCertificate=yes;Uid={user};Pwd={password};\
    ApplicationIntent=ReadOnly"
    engine_str = "mssql+pyodbc:///?odbc_connect={}".format(params)
    return sa.create_engine(engine_str)
