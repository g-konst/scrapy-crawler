import datetime as dt

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


__all__ = ["BaseModel", "CreatedMixin"]


class BaseModel(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"


class CreatedMixin:
    created: Mapped[dt.datetime] = mapped_column(
        default=dt.datetime.now(dt.UTC).replace(tzinfo=None),
        nullable=False,
    )
    updated: Mapped[dt.datetime] = mapped_column(
        default=dt.datetime.now(dt.UTC).replace(tzinfo=None),
        nullable=False,
    )
