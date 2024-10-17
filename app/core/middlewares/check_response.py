import httpx
from scrapy.http import Request as ScrapyRequest, Response as ScrapyResponse
from scrapy.settings import Settings
from scrapy.crawler import Crawler
from scrapy.exceptions import IgnoreRequest

from app.core.spiders import BaseSpider


__all__ = ["CheckResponseMiddleware"]


class CheckResponseMiddleware:
    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(crawler.settings)

    def __init__(self, settings: Settings) -> None:
        self.max_retries = settings.get("RETRY_TIMES", 0)

    def retry(
        self, request: ScrapyRequest, spider: BaseSpider, reason: str
    ) -> ScrapyRequest:
        retry_times = request.meta.get("retry_times", 0) + 1
        spider.logger.info(f"{spider.name} retry {retry_times} for {repr(reason)}")
        if retry_times >= self.max_retries:
            spider.logger.error(f"{spider.name} to many retries")
            raise IgnoreRequest()

        request.meta["retry_times"] = retry_times
        return request

    def process_response(
        self, request: ScrapyRequest, response: ScrapyResponse, spider: BaseSpider
    ) -> ScrapyResponse:
        ok, err = spider.is_valid_response(request, response)
        if not ok:
            return self.retry(request, spider, err)

        return response

    def process_exception(
        self, request: ScrapyRequest, exception: Exception, spider: BaseSpider
    ):
        if isinstance(exception, IgnoreRequest):
            return

        if isinstance(exception, httpx.ReadTimeout):
            return self.retry(request, spider, "retry timeout")

        self.retry(request, spider, repr(exception))
