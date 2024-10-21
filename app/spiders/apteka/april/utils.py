import json

from scrapy.http import Request, Response


class AprilMixin:
    httpx = True
    custom_settings = {
        "RETRY_TIMES": 5,
        "DOWNLOAD_TIMEOUT": 30,
        "COMPRESSION_ENABLED": False,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "X-Requested-With": "XMLHTTPRequest",
            "Referer": "https://apteka-april.ru/",
        },
    }

    def is_valid_response(
        self, request: Request, response: Response
    ) -> tuple[bool, str]:
        try:
            data = json.loads(response.body)
            return bool(data), "empty data"
        except json.JSONDecodeError:
            return False, "json decode error"
        except Exception as e:
            return False, str(e)
