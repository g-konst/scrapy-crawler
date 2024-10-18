import asyncio

from faststream.rabbit import RabbitBroker, RabbitQueue
from twisted.internet import defer, task

from app.core.items import BaseItem
from app.core.spiders import BaseSpider


broker = RabbitBroker()


__all__ = ["AMQPPipeline"]


class AMQPPipeline:
    def __init__(self, rabbitmq_url: str, rabbitmq_queue: str):
        self.rabbitmq_queue = rabbitmq_queue
        self.rabbitmq_url = rabbitmq_url

        self.items_queue = asyncio.Queue()
        self.loop = asyncio.get_event_loop()

        self.processed_count = 0

    # TODO: debug purpose
    def inc(self, *args, **kwargs):
        self.processed_count += 1

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            rabbitmq_url=crawler.settings.get("RABBITMQ_URL"),
            rabbitmq_queue=crawler.settings.get("RABBITMQ_QUEUE"),
        )

    def open_spider(self, spider: BaseSpider):
        defer.Deferred.fromFuture(
            self.loop.create_task(self._connect_to_broker())
        ).addCallback(
            lambda _: spider.logger.info("Connected to RabbitMQ")
        ).addCallback(
            lambda _: task.LoopingCall(self.publish_items, spider).start(0.01)
        )

    async def _connect_to_broker(self):
        broker.url = self.rabbitmq_url
        await broker.connect()
        await broker.declare_queue(RabbitQueue(self.rabbitmq_queue))

    def publish_items(self, spider: BaseSpider):
        if not self.items_queue.empty():
            item = self.items_queue.get_nowait()
            return (
                defer.Deferred.fromFuture(
                    self.loop.create_task(broker.publish(item, self.rabbitmq_queue))
                )
                .addCallback(
                    lambda _: spider.logger.debug(f"Published item: {item['id']}")
                )
                .addCallback(lambda _: self.items_queue.task_done())
                .addCallback(self.inc)
            )

    def close_spider(self, spider: BaseSpider):
        spider.logger.info("Send messages and close spider")
        return (
            defer.Deferred.fromFuture(self.loop.create_task(self.items_queue.join()))
            .addCallback(
                lambda _: spider.logger.info(f"Items processed: {self.processed_count}")
            )
            .addCallback(
                lambda _: defer.Deferred.fromFuture(
                    self.loop.create_task(broker.close())
                ).addCallback(lambda _: spider.logger.info("Broker closed"))
            )
        )

    def process_item(self, item: BaseItem, spider: BaseSpider):
        if getattr(spider, "_table_name", None):
            new_item = item.model_dump()
            new_item["_table_name"] = spider._table_name
            self.items_queue.put_nowait(new_item)
        else:
            return item
