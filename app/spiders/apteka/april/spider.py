import json
from typing import Iterable

from scrapy.http import Request, Response

from app.core.spiders import BaseSpider
from app.core.items import StartItem

from .items import AprilItem
from .utils import AprilMixin


class AprilSpider(AprilMixin, BaseSpider):
    _table_name = "april"

    step = 500  # items per page
    count_url = (
        "https://web-api.apteka-april.ru/catalog"
        "/ID@products?cityID={0}&isAvailable=true"
    )

    items_url = (
        "https://web-api.apteka-april.ru/catalog"
        "/ID,name,price,trademark,properties@products?cityID={city_id}&isAvailable=true:+price[{offset}:{ipp}]"
    )

    # typeID: property
    PROP_MAP = {13: "manufacturer", 15: "country"}

    def start_requests(self) -> Iterable[Request]:
        for city_id in self.params.get("city_ids", []):
            yield Request(
                self.count_url.format(city_id),
                meta={"city_id": city_id},
            )

    def parse(self, response: Response):
        expected = len(json.loads(response.body))
        city_id = response.meta["city_id"]
        self.logger.info(f"Expected: {expected}")
        if expected > 0:
            for start in range(0, expected + 1, self.step):
                yield Request(
                    self.items_url.format(
                        city_id=response.meta["city_id"],
                        offset=start,
                        ipp=self.step,
                    ),
                    callback=self.parse_items,
                    meta={"city_id": city_id},
                )

    def parse_items(self, response: Response):
        data = json.loads(response.body)
        city_id = response.meta["city_id"]
        for item_data in data:
            properties = self.get_props(item_data.get("properties", []))
            yield AprilItem(
                id=item_data["ID"],
                name=item_data["name"],
                price=item_data["price"].get("withoutCard"),
                special_price=item_data["price"].get("withCard"),
                city_id=city_id,
                **{
                    self.PROP_MAP[type_id]: name
                    for type_id, name in properties.items()
                    if type_id in self.PROP_MAP
                },
            )

    def get_props(self, properties: list[dict]) -> dict:
        props = dict()
        for p in properties:
            props[p["typeID"]] = p["name"]
        return props


class AprilCitiesSpider(AprilMixin, BaseSpider):
    _suffix = "cities"
    start_urls = ["https://web-api.apteka-april.ru/gis/cities?hasPharmacies=true"]

    def parse(self, response: Response):
        for data in filter(
            lambda x: x.get("isCity") == True,
            json.loads(response.body),
        ):
            # run new spider for each city
            yield StartItem(
                spider=self.to_name(),
                params={
                    "city_ids": [data["ID"]],
                },
            )
