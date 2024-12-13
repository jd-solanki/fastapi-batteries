# FastAPI Batteries

FastAPI Batteries is a collection of tools and utilities to help you build FastAPI applications faster.

Documentation: [https://fastapi-batteries.github.io/](https://fastapi-batteries.github.io/)

## Features

- 📦 Useful & Common Dependencies like File Validation & Pagination
- ⚠️ Custom Exception
- 🐞 Useful middlewares for debugging & performance tracking
- 🛠️ Utilities

## Requirements

It uses latest Python 3.13 for now but will be add support for Python 3.9+ as well.

It's bit opinionated at starting. This package is primarily focused on following tech stack:

- FastAPI
  - Pydantic
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#usage)
- [SQLAlchemy](https://docs.sqlalchemy.org/) 2.x w/ Declarative Syntax ([Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) via `asyncpg`)
- [Alembic](https://github.com/sqlalchemy/alembic)
- [Postgres](https://www.postgresql.org/)

If you are using something else you probably can't get most of out of this package and you might require opening issue and discuss about it so that we can implement it in this package.

Still, If you're using something else you might find some useful goodies which are not dependent of any stack like:

- [APIException](https://jd-solanki.github.io/fastapi-batteries/fastapi/exceptions/) that follows RFC 9457 which FastAPI don't
- [Request Process Time](https://jd-solanki.github.io/fastapi-batteries/fastapi/middelwares/#request-process-time) middleware
- [Helpful Dependencies](https://jd-solanki.github.io/fastapi-batteries/fastapi/dependencies/)
- More incoming...
