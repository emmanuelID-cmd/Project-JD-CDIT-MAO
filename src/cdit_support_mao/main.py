"""FastAPI entry point for the prototype foundation."""

from fastapi import FastAPI
from pydantic import BaseModel

from cdit_support_mao.database import check_database


class HealthResponse(BaseModel):
    status: str
    database: str


app = FastAPI(
    title="CDIT Support Desk MAO",
    description="Synthetic-data-only prototype foundation; agent workflows are not yet enabled.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Report API availability and local SQLite connectivity."""
    check_database()
    return HealthResponse(status="ok", database="ok")
