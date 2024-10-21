from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import PrimaryKeyConstraint

from app.core.models import AptekaModel


__all__ = ["AprilModel"]


class AprilModel(AptekaModel):
    __tablename__ = "april"

    special_price: Mapped[int | None] = mapped_column()
    city_id: Mapped[int] = mapped_column(default=1, primary_key=True)

    __table_args__ = (
        PrimaryKeyConstraint(
            "id",
            "city_id",
            name="idx_april_pk",
        ),
    )
