import asyncio

from scrapy.spiderloader import SpiderLoader
from scrapy.utils import project, reactor
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.defer import deferred_to_future

# from twisted.internet import reactor as twisted_reactor
from twisted.internet.main import installReactor
from twisted.internet.asyncioreactor import AsyncioSelectorReactor

from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitQueue

from app import settings
from app.core.items import StartItem

reactor.asyncioreactor.install()


class Crawler:
    def __init__(self, broker_url: str, proc: int = 1):
        self._broker = RabbitBroker(
            url=broker_url,
        )
        self._app = FastStream(broker=self.broker)
        self.semaphore = asyncio.Semaphore(proc)

        self.settings = project.get_project_settings()
        self.loader = SpiderLoader.from_settings(self.settings)

        self.process = CrawlerProcess(self.settings)
        self.runner = CrawlerRunner(self.settings)

    @property
    def broker(self) -> RabbitBroker:
        return self._broker

    @property
    def app(self) -> FastStream:
        return self._app

    async def crawl(self, start: StartItem):
        async with self.semaphore:
            spider = self.loader.load(start.spider)
            # TODO: investigate - no requests processed
            await deferred_to_future(self.runner.crawl(spider))
            print("Done crawling", start.spider)

    async def _make_starts(self):
        start_spiders = (
            self.loader.load(name)
            for name in self.loader.list()
            if name.endswith("_start")
        )

        async with self.broker as br:
            await br.declare_queue(RabbitQueue(settings.CRAWLER_START_QUEUE))
            for spider in start_spiders:
                async for item in spider().start():
                    await br.publish(item, settings.CRAWLER_START_QUEUE)


c = Crawler(
    broker_url=settings.RABBITMQ_URL,
    proc=20,
)


@c.broker.subscriber(settings.CRAWLER_START_QUEUE)
async def handle(item: StartItem, msg: RabbitMessage):
    await c.crawl(item)


if __name__ == "__main__":
    import sys

    # TODO: parseargs
    if len(sys.argv) > 1:
        asyncio.run(c._make_starts())
    else:
        asyncio.run(c.app.run())
