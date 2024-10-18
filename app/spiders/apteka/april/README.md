# April spider

Before starting the spider, setup environment and make a migrations to create required tables.

```bash
$ poetry install
$ alembic upgrade head
```

Next run services with docker-compose file.

```bash
$ docker-compose up
```

## Run spider

This spider required `city_ids` list as input parameter

```bash
$ scrapy crawl apteka.april -a params='{"city_ids": [1, 4]}'
```
