from sqlalchemy.ext.declarative import declarative_base

from app.configs.db import Engine

EntityMeta = declarative_base()


def init():
    EntityMeta.metadata.create_all(bind=Engine)
