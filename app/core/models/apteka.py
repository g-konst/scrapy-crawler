from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel, CreatedMixin


__all__ = ["AptekaModel"]


class AptekaModel(CreatedMixin, BaseModel):
    __abstract__ = True
    __tablename__ = None

    name: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    manufacturer: Mapped[str] = mapped_column()
    country: Mapped[str] = mapped_column()
