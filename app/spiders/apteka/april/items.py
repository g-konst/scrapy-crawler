from app.core.items import AptekaItem, BaseItem


class AprilItem(AptekaItem):
    special_price: int | None
    city_id: int

class AprilCityItem(BaseItem):
    name: str
