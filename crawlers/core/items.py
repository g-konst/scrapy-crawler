from pydantic import BaseModel


class AprilItem(BaseModel):
    id: int
    name: str
    price: int
    special_price: int | None
    manufacturer: str
    country: str
