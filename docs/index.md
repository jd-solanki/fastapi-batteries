# Welcome

FastAPI Batteries is a collection of tools and utilities to help you build FastAPI applications faster.

## Why?

In my every FastAPI project I use the same tech stack, tools and utilities. So I decided to create a package that includes all of them.

Here's my tech stack:

- FastAPI
  - Pydantic
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#usage)
- [SQLAlchemy](https://docs.sqlalchemy.org/) 2.x w/ Declarative Syntax ([Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) via `asyncpg`)
- [Alembic](https://github.com/sqlalchemy/alembic)
- [Postgres](https://www.postgresql.org/)

This package is opinionated and it's built around my tech stack. As it evolves we might add more tools and utilities and make it generic enough to be used in any FastAPI project.
