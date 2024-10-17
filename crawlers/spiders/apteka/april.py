import json
from typing import Iterable

from scrapy.http import Request, Response

from crawlers.core.spiders import BaseSpider
from crawlers.core.items import AprilItem


class AprilSpider(BaseSpider):
    custom_settings = {
        "RETRY_TIMES": 5,
        "DOWNLOAD_TIMEOUT": 30,
        "COMPRESSION_ENABLED": False,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "X-Requested-With": "XMLHTTPRequest",
            "Referer": "https://apteka-april.ru/",
        },
    }

    step = 100  # items per page
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

    def is_valid_response(self, request: Request, response: Response) -> bool:
        try:
            data = json.loads(response.body)
            return bool(data), "empty data"
        except json.JSONDecodeError:
            return False, "json decode error"
        except Exception as e:
            return False, str(e)

    def start_requests(self) -> Iterable[Request]:
        for city_id in self.params.get("city_ids", []):
            yield Request(
                self.count_url.format(city_id),
                meta={"city_id": city_id, "httpx": True},
            )

    def parse(self, response: Response):
        expected = len(json.loads(response.body))
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
                    meta={"httpx": True},
                )

    def parse_items(self, response: Response):
        data = json.loads(response.body)
        for item_data in data:
            properties = self.get_props(item_data.get("properties", []))
            yield AprilItem(
                id=item_data["ID"],
                name=item_data["name"],
                price=item_data["price"].get("withoutCard"),
                special_price=item_data["price"].get("withCard"),
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
