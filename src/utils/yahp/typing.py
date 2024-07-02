from typing import TypeVar, Generic

T = TypeVar('T')


class Queryset(Generic[T]):
    """Django Queryset"""
    pass


class User(Generic[T]):
    """Django User"""
    pass
