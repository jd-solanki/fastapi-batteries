from fastapi import FastAPI, status

from fastapi_batteries.fastapi.exceptions import APIException, get_api_exception_handler

app = FastAPI()

app.add_exception_handler(APIException, get_api_exception_handler())


@app.get("/raises-exception/")
async def get_index():
    raise APIException(
        status=status.HTTP_400_BAD_REQUEST,
        title="This is a test exception.",
    )
