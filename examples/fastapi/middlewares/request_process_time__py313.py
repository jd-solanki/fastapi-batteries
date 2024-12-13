from fastapi import FastAPI

from fastapi_batteries.fastapi.middlewares import RequestProcessTimeMiddleware

app = FastAPI()

app.add_middleware(RequestProcessTimeMiddleware)


@app.get("/")
async def get_index():
    return {"message": "Hello World"}
