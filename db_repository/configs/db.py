from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from configs import get_environment_variables
from configs.exceptions import *

env = get_environment_variables()

try:
    DATABASE_URL = f"{env.DATABASE_DIALECT}://{env.DATABASE_USERNAME}:{env.DATABASE_PASSWORD}" \
                   f"@{env.DATABASE_HOSTNAME}:{env.DATABASE_PORT}/{env.DATABASE_NAME}" \
                   f"?options=-c%20search_path={env.DATABASE_SCHEMA}"

    Engine = create_engine(
        DATABASE_URL, echo=env.DEBUG_MODE, future=True
    )

    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=Engine
    )
except Exception as e:
    raise ConfigDatabaseConnectionError(f'Error while creating engine for DB {env.DATABASE_NAME}! '
                                        f'Exception: {e}')


def get_db_connection():
    db = scoped_session(SessionLocal)
    try:
        yield db
    finally:
        db.close()
