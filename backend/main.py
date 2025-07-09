import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.bot.dispatcher import bot, dp
from backend.core.config import FASTAPI_HOST, FASTAPI_PORT
from backend.core.routers_loader import include_all_routers
from backend.models.db_adapter import adapter


async def start_bot():
    logging.info("Starting Telegram bot polling...")
    await dp.start_polling(bot)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await adapter.initialize_tables()
    asyncio.create_task(start_bot())
    yield
    await bot.session.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Blockchain FastAPI",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    include_all_routers(app)
    return app


app = create_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def redirect():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run("main:app", host=FASTAPI_HOST, port=int(FASTAPI_PORT), reload=False)
