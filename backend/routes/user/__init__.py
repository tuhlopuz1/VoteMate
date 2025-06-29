from fastapi import APIRouter
from routes.user.register import router as reg_router
from routes.user.token import router as tok_router

router = APIRouter()

router.include_router(reg_router)
router.include_router(tok_router)
