import asyncio
import logging

from scrapy.settings import Settings
from scrapy.spiderloader import SpiderLoader
from scrapy.utils import project, reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.defer import deferred_to_future

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitQueue

from app.core.items import StartItem

reactor.asyncioreactor.install()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from twisted.internet import reactor as twisted_reactor
from twisted.python import log

settings = project.get_project_settings()


class Crawler:
    def __init__(self, settings: Settings, proc: int = 1):
        self.settings = settings
        self.loader = SpiderLoader.from_settings(self.settings)
        self.runner = CrawlerRunner(self.settings)

        self._broker = RabbitBroker(url=self.settings.get("RABBITMQ_URL"))
        self._app = FastStream(broker=self.broker)
        self.semaphore = asyncio.Semaphore(proc)

    @property
    def broker(self) -> RabbitBroker:
        return self._broker

    @property
    def app(self) -> FastStream:
        return self._app

    async def crawl(self, start: StartItem):
        async with self.semaphore:
            await deferred_to_future(
                self.runner.crawl(
                    start.spider,
                    **start.model_dump(exclude=["spider"]),
                )
            )

    async def _make_starts(self):
        start_queue_name = self.settings.get("CRAWLER_START_QUEUE")
        start_spiders = (
            self.loader.load(name)
            for name in self.loader.list()
            if name.endswith("_start")
        )

        async with self.broker as br:
            await br.declare_queue(RabbitQueue(start_queue_name))
            for spider in start_spiders:
                async for item in spider().start():
                    await br.publish(item, start_queue_name)


c = Crawler(
    proc=12,  # TODO: move to settings
    settings=settings,
)


@c.broker.subscriber(settings.get("CRAWLER_START_QUEUE"))
async def handle(item: StartItem, msg: RabbitMessage):
    # TODO: add logger
    try:
        logger.info(f"Start crawling: {item.model_dump()}")
        await c.crawl(item)
        await msg.ack()
        logger.info(f"Crawled: {item.spider}")
    except Exception as e:
        await msg.nack()
        logger.info(f"Error crawling: {item.spider}, {e}")
        # TODO: add rejection


if __name__ == "__main__":
    import sys

    # TODO: parseargs
    if len(sys.argv) > 1:
        asyncio.run(c._make_starts())
    else:
        log.startLogging(sys.stdout)

        twisted_reactor.callWhenRunning(
            lambda: asyncio.ensure_future(c.app.run())
        )
        twisted_reactor.run()
