import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User
from backend.models.pdf_reports import PDFReportGenerator

router = APIRouter()


@router.get("/send-premium-stats/{poll_id}")
async def send_premium_stats(user: Annotated[User, Depends(check_user)], poll_id: uuid.UUID):
    if not user:
        return badresponse("Unauthorized", 401)
    poll = await adapter.get_by_id(Poll, id=poll_id)
    if not poll:
        return badresponse("Poll not found", 404)
    if poll.user_id != user.id:
        return badresponse("You are not the owner of this poll", 403)
    pdf_path = await PDFReportGenerator.generate_pdf_report(poll_id)
    FileResponse(pdf_path, media_type="application/pdf")
