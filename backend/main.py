from contextlib import asynccontextmanager

import uvicorn
from core.config import FASTAPI_HOST, FASTAPI_PORT
from core.routers_loader import include_all_routers
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from models.db_adapter import adapter


@asynccontextmanager
async def lifespan(app: FastAPI):
    await adapter.initialize_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Shock Video FastAPI",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    include_all_routers(app)
    return app


app = create_app()


@app.get("/")
async def redirect():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run("main:app", host=FASTAPI_HOST, port=int(FASTAPI_PORT), reload=False)
