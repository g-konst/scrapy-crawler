import json
from typing import Optional

from scrapy import Spider
from scrapy.http import Request, Response


class SpiderNameMixin:
    @classmethod
    def _spidermodule(cls):
        return ".".join(cls.__module__.split(".")[2:])

    @property
    def spidernamehead(self):
        return self._spidermodule()


class MetaSpider(type):
    def __init__(cls, clsname, superclasses, attributedict):
        if not attributedict["__module__"].startswith("crawlers.core.spiders"):
            cls.name = "_".join(filter(bool, (cls._spidermodule(),)))


class BaseSpider(SpiderNameMixin, Spider, metaclass=MetaSpider):
    def __init__(
        self, url: Optional[str] = None, params: Optional[dict] = None, *args, **kwargs
    ) -> None:
        self.url = url
        if url:
            self.start_urls = [url]

        if params and not isinstance(params, dict):
            params = json.loads(params)
        self.params = params

    def is_valid_response(
        self, request: Request, response: Response
    ) -> tuple[bool, str]:
        return True, None
