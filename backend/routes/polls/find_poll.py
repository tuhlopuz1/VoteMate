from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends

from backend.core.dependencies import badresponse, check_user
from backend.models.db_adapter import adapter
from backend.models.db_tables import Poll, User, Vote
from backend.models.schemas import PollSchema, SearchPollSchema

router = APIRouter()


async def check_poll_status(poll: Poll, poll_status: Optional[str]) -> bool:
    """Проверяет статус опроса (open/closed)"""
    now = datetime.now(timezone.utc)
    if poll_status in ["all", None]:
        return True
    if poll_status == "open" and poll.start_date <= now <= poll.end_date:
        return True
    if poll_status == "closed" and now > poll.end_date:
        return True
    return False


async def check_vote_status(poll: Poll, vote_status: Optional[str], user_id: UUID) -> bool:
    """Проверяет статус голосования пользователя"""
    if vote_status in ["all", None]:
        return True

    # Проверяем, голосовал ли пользователь в этом опросе
    vote = await adapter.get_by_values(Vote, {"user_id": user_id, "poll_id": poll.id})
    has_voted = vote is not None

    if vote_status == "voted" and has_voted:
        return True
    if vote_status == "not_voted" and not has_voted:
        return True
    return False


async def prepare_poll_response(poll: Poll, user: User) -> PollSchema:
    """Подготавливает опрос для ответа, учитывая права доступа"""
    now = datetime.now(timezone.utc)
    poll_sch = PollSchema.model_validate(poll)

    # Устанавливаем флаги
    try:
        poll_sch.is_active = poll["start_date"] <= now <= poll["end_date"]
        poll_sch.is_voted = (
            await adapter.get_by_values(Vote, {"user_id": user.id, "poll_id": poll["id"]})
            is not None
        )
        if user.id != poll["user_id"] and now < poll["end_date"]:
            poll_sch.options = list(poll.options.keys()) if poll.options else []
    except Exception:
        poll_sch.is_active = poll.start_date <= now <= poll.end_date
        poll_sch.is_voted = (
            await adapter.get_by_values(Vote, {"user_id": user.id, "poll_id": poll.id}) is not None
        )
        if user.id != poll.user_id and now < poll.end_date:
            poll_sch.options = list(poll.options.keys()) if poll.options else []

    return poll_sch


@router.post("/search-polls")
async def search_polls(user: Annotated[User, Depends(check_user)], search_params: SearchPollSchema):
    if not user:
        return badresponse("Unauthorized", 401)

    # Валидация параметров
    if search_params.voting_status not in ["all", "voted", "not_voted", None]:
        return badresponse("Invalid voting status", 400)
    if search_params.sort_by not in ["popularity_asc", "popularity_desc", None]:
        return badresponse("Invalid sorting", 400)
    if search_params.poll_status not in ["all", "open", "closed", None]:
        return badresponse("Invalid poll status", 400)

    # Поиск по имени если задан
    if search_params.poll_name:
        polls = await adapter.find_similar_value(
            Poll, "name", search_params.poll_name, similarity_threshold=40
        )
    else:
        polls = await adapter.get_all(Poll)

    # Применяем фильтры
    filtered_polls = []
    for poll in polls:
        # Проверка приватности: не приватные или созданные пользователем
        try:
            if not poll["private"] and poll["user_id"] != user.id:
                continue
        except Exception:
            if not poll.private and poll.user_id != user.id:
                continue
        # Проверка статуса опроса
        if not await check_poll_status(poll, search_params.poll_status):
            continue

        # Проверка статуса голосования
        if not await check_vote_status(poll, search_params.voting_status, user.id):
            continue

        # Проверка тегов
        if search_params.tags:
            try:
                poll_tags = poll["hashtags"] or []
            except Exception:
                poll_tags = poll.hashtags or []
            if not set(search_params.tags).issubset(poll_tags):
                continue

        filtered_polls.append(poll)

    # Применяем сортировку
    if search_params.sort_by == "popularity_asc":
        try:
            filtered_polls.sort(key=lambda x: x["votes_count"])
        except Exception:
            filtered_polls.sort(key=lambda x: x.votes_count)
    elif search_params.sort_by == "popularity_desc":
        try:
            filtered_polls.sort(key=lambda x: x["votes_count"], reverse=True)
        except Exception:
            filtered_polls.sort(key=lambda x: x.votes_count, reverse=True)

    # Подготавливаем ответ
    result = [await prepare_poll_response(poll, user) for poll in filtered_polls]
    return result
