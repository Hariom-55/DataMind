import os

from fastapi import Header, HTTPException


INTERNAL_API_KEY = os.getenv("DATAMIND_INTERNAL_API_KEY")


def require_internal_api_key(
    x_internal_api_key: str | None = Header(default=None),
) -> None:
    if not INTERNAL_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Internal API authentication is not configured",
        )

    if x_internal_api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )