from scrapy import signals
from faststream.rabbit import RabbitBroker, RabbitQueue

from app.core.items import BaseItem, StartItem
from app.core.spiders import BaseSpider


__all__ = ["AMQPPipeline"]


class AMQPPipeline:
    def __init__(
        self,
        rabbitmq_url: str,
        rabbitmq_queue: str,
        crawler_start_queue: str,
    ):
        self.rabbitmq_queue = rabbitmq_queue
        self.rabbitmq_url = rabbitmq_url
        self.crawler_start_queue = crawler_start_queue
        self.broker = RabbitBroker(self.rabbitmq_url)

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(
            rabbitmq_url=crawler.settings.get("RABBITMQ_URL"),
            rabbitmq_queue=crawler.settings.get("RABBITMQ_QUEUE"),
            crawler_start_queue=crawler.settings.get("CRAWLER_START_QUEUE"),
        )
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)

        return s

    async def spider_opened(self, spider: BaseSpider):
        await self.broker.connect()
        await self.broker.declare_queue(RabbitQueue(self.rabbitmq_queue))
        await self.broker.declare_queue(RabbitQueue(self.crawler_start_queue))
        spider.logger.info("Connected to RabbitMQ")

    async def spider_closed(self, spider: BaseSpider):
        spider.logger.info("Spider closed")
        await self.broker.close()
        spider.logger.info("Broker closed")

    async def process_item(self, item: BaseItem, spider: BaseSpider):
        spider.logger.info(f"Processing item: {item.model_dump()}")
        if isinstance(item, StartItem):
            await self.broker.publish(item, self.crawler_start_queue)
        elif isinstance(item, BaseItem):
            if getattr(spider, "_table_name", None):
                new_item = item.model_dump()
                new_item["_table_name"] = spider._table_name
                await self.broker.publish(new_item, self.rabbitmq_queue)
        return item
