from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import AptekaModel


__all__ = ["AprilModel"]


class AprilModel(AptekaModel):
    __tablename__ = "april"

    special_price: Mapped[int | None] = mapped_column()
    city_id: Mapped[int] = mapped_column(default=1)
