from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from fastapi_batteries.fastapi.middlewares import QueryCountMiddleware

app = FastAPI()


engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)


app.add_middleware(QueryCountMiddleware, engine=engine)


@app.get("/")
async def get_index():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
        await conn.commit()

        return {"message": "Hello World"}
