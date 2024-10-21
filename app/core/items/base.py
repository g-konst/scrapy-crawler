from typing import Optional

from pydantic import BaseModel


__all__ = ["BaseItem", "StartItem"]


class BaseItem(BaseModel):
    _table_name: str

    class Config:
        from_attributes = True

    id: int


class StartItem(BaseModel):
    spider: str
    url: Optional[str] = None
    params: Optional[dict] = None
