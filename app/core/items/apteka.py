from .base import BaseItem


__all__ = ["AptekaItem"]


class AptekaItem(BaseItem):
    name: str
    price: int

    country: str
    manufacturer: str
