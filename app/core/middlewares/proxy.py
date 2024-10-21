from scrapy.http import Request

from app.core.spiders import BaseSpider


__all__ = ["ProxyMiddleware"]


class ProxyMiddleware:
    async def get_proxy(self):
        # TODO: add proxy service
        return "http://127.0.0.1:1080"

    async def process_request(self, request: Request, spider: BaseSpider):
        if request.meta.pop("renew_proxy", False):
            spider.logger.info("Renew proxy")
            request.meta["proxy"] = await self.get_proxy()

        if "proxy" not in request.meta:
            spider.logger.info("No proxy found, set proxy")
            request.meta["proxy"] = await self.get_proxy()
