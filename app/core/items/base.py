from pydantic import BaseModel


__all__ = ["BaseItem"]


class BaseItem(BaseModel):
    _table_name: str

    class Config:
        from_attributes = True

    id: int
