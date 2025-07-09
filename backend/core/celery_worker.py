import logging

from celery import Celery

from backend.core.config import CELERY_REDIS

logger = logging.getLogger(__name__)

logger.info(CELERY_REDIS)
celery_app = Celery("worker", broker=CELERY_REDIS, backend=CELERY_REDIS)

celery_app.autodiscover_tasks(["backend.routes.polls"])
