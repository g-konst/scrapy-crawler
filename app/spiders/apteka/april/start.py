from app.core.spiders import BaseStartSpider
from app.core.items import StartItem


class StartSpider(BaseStartSpider):
    async def start(self):
        yield StartItem(
            spider="apteka.april_cities",
        )
