from scrapy.http import Request

from app.core.spiders import BaseSpider


__all__ = ["ProxyMiddleware"]


class ProxyMiddleware:
    async def get_proxy(self):
        # TODO: add proxy service
        return None

    async def process_request(self, request: Request, spider: BaseSpider):
        request = await spider.make_request(request)

        if request.meta.pop("renew_proxy", False):
            spider.logger.info("Renew proxy")
            request.meta["proxy"] = await self.get_proxy()

        if "proxy" not in request.meta:
            spider.logger.info("No proxy found, set proxy")
            request.meta["proxy"] = await self.get_proxy()
