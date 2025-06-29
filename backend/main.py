from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from models.db_adapter import adapter
from routes.user import router as user_router
from contextlib import asynccontextmanager
import uvicorn

from config import FASTAPI_HOST, FASTAPI_PORT

@asynccontextmanager
async def lifespan(app: FastAPI):
    await adapter.initialize_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router, tags=["User"])


@app.get("/")
async def redirect():
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run("main:app", host=FASTAPI_HOST, port=int(FASTAPI_PORT), reload=False)
