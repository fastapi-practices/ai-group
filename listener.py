from collections.abc import Collection
from typing import Any

import sqlalchemy as sa

from sqlalchemy import Select
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.sql import visitors
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.schema import Table

from backend.plugin.ai_buddy.model import AIMcp, AIModel, AIProvider
from backend.plugin.ai_buddy_group.enums import AIGroupResourceScopeType, AIGroupResourceType
from backend.plugin.ai_buddy_group.model import AIGroup, AIGroupResource, AIGroupUser

AI_GROUP_RESOURCE_MODEL_CLASSES = frozenset({AIProvider, AIModel, AIMcp})
AI_GROUP_RESOURCE_TABLE_MODEL_MAP = {model.__tablename__: model for model in AI_GROUP_RESOURCE_MODEL_CLASSES}


def get_statement_ai_group_resource_models(statement: Select[Any]) -> set[type[Any]]:
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


def build_ai_group_resource_visibility_criteria(
    *,
    user_id: int,
    resource_id: Any,
    resource_type: AIGroupResourceType,
) -> ColumnElement[bool]:
    """
    构建 AI 分组资源可见性过滤条件

    :param user_id: 用户 ID
    :param resource_id: 资源 ID 字段
    :param resource_type: AI 分组资源类型
    :return:
    """
    user_group_exists = sa.exists().where(
        AIGroupUser.user_id == user_id,
        AIGroupUser.deleted == 0,
        AIGroup.id == AIGroupUser.group_id,
        AIGroup.deleted == 0,
    )
    all_visible_exists = sa.exists().where(
        AIGroupUser.user_id == user_id,
        AIGroupUser.deleted == 0,
        AIGroup.id == AIGroupUser.group_id,
        AIGroup.deleted == 0,
        AIGroupResource.group_id == AIGroup.id,
        AIGroupResource.deleted == 0,
        AIGroupResource.resource_type == resource_type.value,
        AIGroupResource.scope_type == AIGroupResourceScopeType.all.value,
    )
    specified_visible_exists = sa.exists().where(
        AIGroupUser.user_id == user_id,
        AIGroupUser.deleted == 0,
        AIGroup.id == AIGroupUser.group_id,
        AIGroup.deleted == 0,
        AIGroupResource.group_id == AIGroup.id,
        AIGroupResource.deleted == 0,
        AIGroupResource.resource_type == resource_type.value,
        AIGroupResource.scope_type == AIGroupResourceScopeType.specified.value,
        AIGroupResource.resource_id == resource_id,
    )
    return sa.or_(sa.not_(user_group_exists), all_visible_exists, specified_visible_exists)


def apply_ai_group_visibility_criteria(
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

    if AIProvider in resource_models:
        provider_criteria = build_ai_group_resource_visibility_criteria(
            user_id=user_id,
            resource_id=AIProvider.id,
            resource_type=AIGroupResourceType.provider,
        )
        options.append(with_loader_criteria(AIProvider, provider_criteria, include_aliases=True))
    if AIModel in resource_models:
        model_provider_criteria = build_ai_group_resource_visibility_criteria(
            user_id=user_id,
            resource_id=AIModel.provider_id,
            resource_type=AIGroupResourceType.provider,
        )
        model_criteria = build_ai_group_resource_visibility_criteria(
            user_id=user_id,
            resource_id=AIModel.id,
            resource_type=AIGroupResourceType.model,
        )
        options.append(
            with_loader_criteria(AIModel, sa.and_(model_provider_criteria, model_criteria), include_aliases=True)
        )
    if AIMcp in resource_models:
        mcp_criteria = build_ai_group_resource_visibility_criteria(
            user_id=user_id,
            resource_id=AIMcp.id,
            resource_type=AIGroupResourceType.mcp,
        )
        options.append(with_loader_criteria(AIMcp, mcp_criteria, include_aliases=True))

    if not options:
        return statement
    return statement.options(*options)
