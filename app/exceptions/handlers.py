from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


async def integrity_error_handler(
    request: Request,
    exc: IntegrityError,
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "La operación entra en conflicto con información existente.",
            "error": "conflict",
        },
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = []

    for error in exc.errors():
        clean_error = {
            "type": error.get("type"),
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "input": error.get("input"),
        }

        if "ctx" in error:
            ctx = error["ctx"]

            clean_ctx = {}

            for key, value in ctx.items():
                clean_ctx[key] = str(value)

            clean_error["ctx"] = clean_ctx

        errors.append(clean_error)

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Los datos enviados no son válidos.",
            "error": "validation_error",
            "errors": errors,
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Ha ocurrido un error interno en el servidor.",
            "error": "internal_server_error",
        },
    )