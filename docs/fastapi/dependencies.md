# Dependencies

FastAPI Batteries comes with some handful dependencies that are common in most FastAPI projects.

## File Validator

This dependency uses [python-magic](https://pypi.org/project/python-magic/) to accurately determine the file type of the uploaded file.

You can use this validator to:

- Validate the file type (via mime type)
- Validate File Size

=== "Example"

    ```py hl_lines="5-6 11-16 20"
    --8<-- "examples/fastapi/dependencies/file_validator__py313.py"
    ```

=== "Preview"

    ![fastapi_batteries__file_validator_mime_type_err](../assets/images/examples/fastapi/dependencies/file_validator_mime_type_err.png)

## Pagination Query Params

FastAPI allows using [Pydantic model as query parameter model](https://fastapi.tiangolo.com/tutorial/query-param-models/).

Thanks to that you can have reusable pagination query parameters. This is minimal but faster and when you pair it with our CRUD helper it becomes more powerful.

=== "Example"

    ```py hl_lines="5 11 16"
    --8<-- "examples/fastapi/dependencies/pagination__py313.py"
    ```

=== "Preview"

    ![fastapi_batteries__pagination_ss](../assets/images/examples/fastapi/dependencies/pagination_ss.png)
