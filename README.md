# Scrapy crawler

A Scrapy-based web crawler with an AMQP pipeline and a FastStream consumer.

## Project Setup

This project uses the `poetry` tool for dependency management.

### Setting Up the Environment

To set up the virtual environment and install dependencies, run the following commands:

```bash
$ python3 -m venv .venv
$ poetry use .venv/bin/python
$ poetry install
```

### Building the Wheels Package

To build the project as a wheels package, use this command:

```bash
$ poetry build
```


## Crawler Structure

All spider files should be organized in separate folders. A typical structure might look like this:

```tree
app
└─ spiders
   └─ spider-group
      └── my-spider-dir
          ├── __init__.py
          ├── models.py
          ├── items.py
          └── spider.py
```

Ensure that `<my-spider-dir>` is included in the `__init__.py` file of the `<spider-group>` module.

### Database Migrations

After your spiders are set up, create database migrations to generate any required tables:

```bash
$ alembic revision --autogenerate -m "Add new spider"
$ alembic upgrade head
```

### Running Services

To run all necessary services, use docker-compose. Feel free to adjust environment settings in the `docker-compose.yml` file:


```shell
$ docker-compose up
```

## Running the Crawler

### Listing Available Spiders

To list all available spiders, use the following command:

```bash
$ scrapy list
```

You should see output similar to this:

```bash
spider-group.my-spider-dir
```

### Starting the Crawler

To run a specific spider, use this command:

```bash
$ scrapy crawl spider-group.my-spider-dir
```

### Passing Additional Parameters

You can also pass additional parameters in JSON format for use in your spider:


```bash
$ scrapy crawl <spider-name> -a params='{"some": "data"}'
```

## Using httpx with Scrapy

Scrapy doesn't support TLSv1.3 by default. If you need this feature, you can use the `httpx` downloader. To do so, pass `"httpx": True` in the `Request` meta:

```python
Request(url, meta={"httpx": True})
```

## TODO

 - [ ] - Proxy Middleware: Add proxy middleware to handle requests via proxies.
 - [ ] - Implement comprehensive unit tests for spiders, pipelines, and consumers.
 - [ ] - Add error handling to the AMQP pipeline to ensure message delivery failures are logged and retried.
 - [ ] - Optimize database queries in the pipeline, including bulk inserts and updates to reduce overhead.
 - [ ] - Improve logging: Set up more detailed logs to monitor crawler performance, including timeouts, retries, and missing fields.
 - [ ] - Enhance the FastStream consumer: Add concurrency support and ensure the consumer can handle high-throughput scenarios.
 - [ ] - Add support for custom middlewares to the Scrapy spiders for enhanced request processing.
 - [ ] - Set up CI/CD pipeline for automated testing and deployment using GitHub Actions or another CI tool.
 - [ ] - Add documentation for adding new spiders, including example configurations.
 - [ ] - Refactor spider models and items to simplify data management and ensure consistency across different spider groups.
