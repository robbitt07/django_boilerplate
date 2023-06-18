from decouple import Config, RepositoryEnv
import psycopg2

config = Config(RepositoryEnv(".env"))

## Get Database Config
conn = psycopg2.connect(
    user=config("DB_USER"),
    password=config("DB_PASSWORD"),
    host=config("DB_HOST"),
    port=config("DB_PORT", cast=str)
)

## Database functions cannot be done within a transaction block
conn.autocommit = True

db_name = config("DB_NAME")


def execute_psql(sql, conn):
    with conn, conn.cursor() as csr:
        csr.execute(sql)


## --- Check if database exists and save result to **database_exists** ---
check_database_exists_sql = f"""
select exists (SELECT datname
			FROM pg_catalog.pg_database 
				WHERE lower(datname) = lower("{db_name}")
				)
"""
with conn.cursor() as csr:
    csr.execute(check_database_exists_sql)
    database_exists = csr.fetchone()[0]

# --- Check if database exists, drop if it exists ---
if database_exists:
    stop_connectivity_database_sql = f"""
    select
        pg_terminate_backend (pg_stat_activity.pid)
    from pg_stat_activity
        where pg_stat_activity.datname = "{db_name}";
    """

    drop_database_sql = f"""
    drop database {db_name};
    """

    # Drop Database Execute
    execute_psql(stop_connectivity_database_sql, conn)
    execute_psql(drop_database_sql, conn)


# --- Create database ----------------------------------------------------------
create_database_sql = f"""
create database {db_name};
"""
# Create Database Execute
execute_psql(create_database_sql, conn)
