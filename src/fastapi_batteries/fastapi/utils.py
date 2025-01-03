import re
import warnings

from fastapi import FastAPI
from fastapi.routing import APIRoute


def use_route_path_as_operation_ids(
    app: FastAPI,
    *,
    warn_on_func_name_mismatch: bool = False,
) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute):
            normalized_path_format = re.sub(r"\W", "_", route.path_format)
            method_name = next(iter(route.methods)).lower()

            # NOTE: We intentionally preserved double underscore in the operation_id to indicate that anything around `__` is path parameter  # noqa: E501
            route.operation_id = f"{method_name}{normalized_path_format}".strip("_")

            if warn_on_func_name_mismatch and route.operation_id != route.name:
                warnings.warn(
                    f'Route "{route.path_format}" has the function name "{route.name}" '
                    f'which does not match expected operation ID: "{route.operation_id}"',
                    stacklevel=2,
                )
