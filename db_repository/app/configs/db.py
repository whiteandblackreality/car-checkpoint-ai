from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.configs import get_environment_variables
from app.configs.exceptions import *
from app.logger import logger

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

    logger.info(f'Connect to {env.DATABASE_NAME} DB, {env.DATABASE_SCHEMA} schema')

except Exception as e:
    raise ConfigDatabaseConnectionError(f'Error while creating engine for DB {env.DATABASE_NAME}! '
                                        f'Exception: {e}')


def get_db_connection():
    db = scoped_session(SessionLocal)
    try:
        yield db
    finally:
        db.close()
