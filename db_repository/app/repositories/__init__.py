from abc import abstractmethod
from typing import Generic, List, TypeVar

from sqlalchemy.exc import PendingRollbackError

from app.configs.db import get_db_connection

M = TypeVar("M")

K = TypeVar("K")


class RepositoryMeta(Generic[M, K]):

    @abstractmethod
    def create(self, instance: M) -> M:
        pass

    @abstractmethod
    def delete(self, id: K) -> None:
        pass

    @abstractmethod
    def get(self, id: K) -> M:
        pass

    @abstractmethod
    def list(self, limit: int, start: int) -> List[M]:
        pass


def decorator_rollback_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PendingRollbackError:
            args[0].db = next(get_db_connection(is_rollback=True))
            return func(*args, **kwargs)
    return wrapper
