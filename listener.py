from collections.abc import Collection
from typing import Any

import sqlalchemy as sa

from sqlalchemy import Select
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.sql import visitors
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.schema import Table

from backend.plugin.ai_buddy.model import AIBuddyMcp, AIBuddyModel, AIBuddyProvider
from backend.plugin.ai_buddy_group.enums import AIBuddyResourceScopeType, AIBuddyResourceType
from backend.plugin.ai_buddy_group.model import AIBuddyGroup, AIBuddyResource, AIBuddyUser

AI_GROUP_RESOURCE_MODEL_CLASSES = frozenset({AIBuddyProvider, AIBuddyModel, AIBuddyMcp})
AI_GROUP_RESOURCE_TABLE_MODEL_MAP = {model.__tablename__: model for model in AI_GROUP_RESOURCE_MODEL_CLASSES}


def get_statement_ai_buddy_resource_models(statement: Select[Any]) -> set[type[Any]]:
    """
    获取查询涉及的 AI 分组可控资源模型

    :param statement: SQLAlchemy 查询表达式
    :return:
    """
    resource_models: set[type[Any]] = set()
    for element in visitors.iterate(statement):
        if isinstance(element, Table):
            resource_model = AI_GROUP_RESOURCE_TABLE_MODEL_MAP.get(element.name)
            if resource_model is not None:
                resource_models.add(resource_model)
    return resource_models


def build_ai_buddy_resource_visibility_criteria(
    *,
    user_id: int,
    resource_id: Any,
    resource_type: AIBuddyResourceType,
) -> ColumnElement[bool]:
    """
    构建 AI 分组资源可见性过滤条件

    :param user_id: 用户 ID
    :param resource_id: 资源 ID 字段
    :param resource_type: AI 分组资源类型
    :return:
    """
    user_group_exists = sa.exists().where(
        AIBuddyUser.user_id == user_id,
        AIBuddyUser.deleted == 0,
        AIBuddyGroup.id == AIBuddyUser.group_id,
        AIBuddyGroup.deleted == 0,
    )
    all_visible_exists = sa.exists().where(
        AIBuddyUser.user_id == user_id,
        AIBuddyUser.deleted == 0,
        AIBuddyGroup.id == AIBuddyUser.group_id,
        AIBuddyGroup.deleted == 0,
        AIBuddyResource.group_id == AIBuddyGroup.id,
        AIBuddyResource.deleted == 0,
        AIBuddyResource.resource_type == resource_type.value,
        AIBuddyResource.scope_type == AIBuddyResourceScopeType.all.value,
    )
    specified_visible_exists = sa.exists().where(
        AIBuddyUser.user_id == user_id,
        AIBuddyUser.deleted == 0,
        AIBuddyGroup.id == AIBuddyUser.group_id,
        AIBuddyGroup.deleted == 0,
        AIBuddyResource.group_id == AIBuddyGroup.id,
        AIBuddyResource.deleted == 0,
        AIBuddyResource.resource_type == resource_type.value,
        AIBuddyResource.scope_type == AIBuddyResourceScopeType.specified.value,
        AIBuddyResource.resource_id == resource_id,
    )
    return sa.or_(sa.not_(user_group_exists), all_visible_exists, specified_visible_exists)


def apply_ai_buddy_group_visibility_criteria(
    statement: Select[Any],
    *,
    user_id: int,
    resource_models: Collection[type[Any]],
    is_superuser: bool = False,
) -> Select[Any]:
    """
    为 AI 资源查询追加分组可见性过滤条件

    :param statement: SQLAlchemy 查询表达式
    :param user_id: 用户 ID
    :param resource_models: 查询涉及的 AI 分组可控资源模型
    :param is_superuser: 是否超级管理员
    :return:
    """
    if is_superuser:
        return statement
    options = []

    if AIBuddyProvider in resource_models:
        provider_criteria = build_ai_buddy_resource_visibility_criteria(
            user_id=user_id,
            resource_id=AIBuddyProvider.id,
            resource_type=AIBuddyResourceType.provider,
        )
        options.append(with_loader_criteria(AIBuddyProvider, provider_criteria, include_aliases=True))
    if AIBuddyModel in resource_models:
        model_provider_criteria = build_ai_buddy_resource_visibility_criteria(
            user_id=user_id,
            resource_id=AIBuddyModel.provider_id,
            resource_type=AIBuddyResourceType.provider,
        )
        model_criteria = build_ai_buddy_resource_visibility_criteria(
            user_id=user_id,
            resource_id=AIBuddyModel.id,
            resource_type=AIBuddyResourceType.model,
        )
        options.append(
            with_loader_criteria(AIBuddyModel, sa.and_(model_provider_criteria, model_criteria), include_aliases=True)
        )
    if AIBuddyMcp in resource_models:
        mcp_criteria = build_ai_buddy_resource_visibility_criteria(
            user_id=user_id,
            resource_id=AIBuddyMcp.id,
            resource_type=AIBuddyResourceType.mcp,
        )
        options.append(with_loader_criteria(AIBuddyMcp, mcp_criteria, include_aliases=True))

    if not options:
        return statement
    return statement.options(*options)
