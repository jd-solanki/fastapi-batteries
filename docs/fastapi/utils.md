# Utils

We've added bunch of utilities to help you build the FastAPI project faster.

## `use_route_path_as_operation_ids`

This utility won't speed up your development but instead it will ease life of frontend developer (or you if you're full stack developer) using your OpenAPI specs via [generate clients (or SDK)](https://fastapi.tiangolo.com/advanced/generate-clients/). By default, FastAPI generates [operation ids](https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/?h=operation#openapi-operationid) automatically.

For example, You generated TypeScript types from OpenAPI specs and you'll use type like this: `type FRONTEND_TYPE = APIResponse<'your_operation_id', 200>`. Here, `APIResponse` is TypeScript's utility type that extract actual response type for given status code (in this case `200`). Thanks to this, Whenever you change response schema in FastAPI your frontend will be aware of new schema without manually writing any code.

I really like this linked schemas as this allows safety while writing frontend code which is completely decoupled from backend. Fun Fact, I fixed bug without running actual frontend & backend servers thanks to this linked schemas and guess what it resolved bug in production successfully. Kinda risky but I'm proud of it and tell this to everyone including you know 😉

<br>

Here's the default behavior.

```py
@app.get("/")
def get_index():
    return {"Hello": "World"}
```

For above operation, FastAPI will generate `get_index__get` as operation id. However, frontend developer won't know that `/` (root or index) API endpoint's operation id is `get_index__get` without looking at the source code and knowing the convention (`FUNC_NAME` + `__` + `HTTP_METHOD` most probably).

This utility function will help you generate predictable operation id because it generates id based on route path which frontend (or you if you're full stack) dev already knows.

For the same operation above, `use_route_path_as_operation_ids` will generate `get_` as operation id.

Here's convention: `HTTP_METHOD` + `_` + `ROUTE_PATH` (+ `__PARAM__` if path has parameter)

```py hl_lines="3 33"
from fastapi import FastAPI

from fastapi_batteries.fastapi.utils import use_route_path_as_operation_ids

app = FastAPI()


@app.get("/")
async def get_index():
    return {"operation id": "get"}


@app.post("/items")
async def post_items():
    return {"operation id": "post_items"}


@app.get("/items")
async def get_items():
    return {"operation id": "get_items"}


@app.get("/items/{item_id}")
async def get_item():
    return {"operation id": "get_items__item_id"}


@app.get("/items/{item_id}/sub_item")
async def get_item_subitem():
    return {"operation id": "get_items__item_id__sub_item"}


use_route_path_as_operation_ids(app)
```

!!! warning

    Ensure, You always use this util after defining or including all of your operations (This is also [stated](https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#openapi-operationid) in official FastAPI docs).
