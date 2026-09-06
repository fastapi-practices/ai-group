from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.plugin.ai_buddy.agent.policy.base import AIResourcePolicy
from backend.plugin.ai_buddy.agent.policy.context import AIInvocationContext
from backend.plugin.ai_buddy_group.crud.crud_group import ai_group_dao
from backend.plugin.ai_buddy_group.crud.crud_resource import ai_group_resource_dao
from backend.plugin.ai_buddy_group.crud.crud_user import ai_group_user_dao
from backend.plugin.ai_buddy_group.enums import AIGroupResourceScopeType, AIGroupResourceType
from backend.plugin.ai_buddy_group.model import AIGroupResource


class AIGroupResourcePolicy(AIResourcePolicy):
    """AI 分组资源策略"""

    @staticmethod
    def _resolve_ids(
        *,
        resources: Sequence[AIGroupResource],
        resource_type: AIGroupResourceType,
    ) -> frozenset[int] | None:
        """
        计算分组指定资源 ID

        :param resources: AI 分组资源列表
        :param resource_type: AI 分组资源类型
        :return:
        """
        matched_resources = [resource for resource in resources if resource.resource_type == resource_type.value]
        if not matched_resources:
            return None
        if any(resource.scope_type == AIGroupResourceScopeType.all.value for resource in matched_resources):
            return None
        return frozenset(
            resource.resource_id
            for resource in matched_resources
            if resource.scope_type == AIGroupResourceScopeType.specified.value
        )

    async def before_invoke(self, *, db: AsyncSession, context: AIInvocationContext) -> None:
        """
        AI 调用前校验分组资源范围

        :param db: 数据库会话
        :param context: AI 调用策略上下文
        :return:
        """
        if context.is_superuser:
            return
        group_ids = await ai_group_user_dao.get_group_ids_by_user(db, context.user_id)
        if not group_ids:
            return
        groups = await ai_group_dao.get_by_ids(db, group_ids)
        if not groups:
            return
        resources = await ai_group_resource_dao.get_by_group_ids(db, group_ids)
        provider_ids = self._resolve_ids(
            resources=resources,
            resource_type=AIGroupResourceType.provider,
        )
        model_ids = self._resolve_ids(
            resources=resources,
            resource_type=AIGroupResourceType.model,
        )
        mcp_ids = self._resolve_ids(
            resources=resources,
            resource_type=AIGroupResourceType.mcp,
        )
        if provider_ids is not None and context.provider_id not in provider_ids:
            raise errors.AuthorizationError(msg='当前用户无权使用此供应商')
        if model_ids is not None and context.model_pk not in model_ids:
            raise errors.AuthorizationError(msg='当前用户无权使用此模型')
        if mcp_ids is not None and any(mcp_id not in mcp_ids for mcp_id in context.mcp_ids):
            raise errors.AuthorizationError(msg='当前用户无权使用指定 MCP')


ai_group_resource_policy: AIGroupResourcePolicy = AIGroupResourcePolicy()
