from fastapi import APIRouter

from backend.core.conf import settings
from backend.plugin.ai_buddy_group.api.v1.group import router as group_router

v1 = APIRouter(prefix=settings.FASTAPI_API_V1_PATH)

v1.include_router(group_router, prefix='/ai-groups', tags=['AI 分组管理'])
