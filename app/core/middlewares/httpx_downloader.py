import httpx
from scrapy import signals
from scrapy.http import Request as ScrapyRequest, Response as ScrapyResponse

from app.core.spiders import BaseSpider


__all__ = ["HttpxDownloaderMiddleware"]


class HttpxDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls(crawler.settings)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def __init__(self, settings):
        self.client = httpx.AsyncClient()
        self.request_timeout = settings.get("DOWNLOAD_TIMEOUT", 30)

    async def spider_closed(self, spider: BaseSpider):
        spider.logger.info("Closing httpx client")
        await self.client.aclose()

    async def process_request(self, request: ScrapyRequest, spider: BaseSpider):
        if getattr(spider, "httpx", None) or request.meta.get("httpx") == True:
            spider.logger.info(f"Fetching {request.url} using httpx")
            response = await self.client.send(request=self._to_httpx_request(request))

            if response.is_error:
                spider.logger.error(
                    f"Error fetching {request.url}: {response.status_code}"
                )
                raise httpx.RequestError(f"Bad response: {response.status_code}")

            return self._to_scrapy_response(response, request)

    def _parse_headers(self, headers: dict) -> dict:
        return {k: v[0] if isinstance(v, list) else v for k, v in headers.items()}

    def _to_httpx_request(self, request: ScrapyRequest) -> httpx.Request:
        return self.client.build_request(
            method=request.method,
            url=request.url,
            data=request.body,
            headers=self._parse_headers(request.headers),
            cookies=request.cookies,
            timeout=self.request_timeout,
        )

    def _to_scrapy_response(
        self, response: httpx.Response, request: ScrapyRequest
    ) -> ScrapyResponse:
        return ScrapyResponse(
            url=str(response.url),
            status=response.status_code,
            headers=dict(response.headers),
            body=response.content,
            request=request,
        )
