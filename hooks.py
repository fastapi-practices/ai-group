from typing import Any, cast

from fastapi import FastAPI
from sqlalchemy import Select, event
from sqlalchemy.orm import ORMExecuteState, Session

from backend.common.context import ctx
from backend.plugin.ai_buddy.agent.policy.registry import register_ai_buddy_resource_policy
from backend.plugin.ai_buddy_group.listener import (
    AI_GROUP_RESOURCE_MODEL_CLASSES,
    apply_ai_buddy_group_visibility_criteria,
    get_statement_ai_buddy_resource_models,
)
from backend.plugin.ai_buddy_group.policy.resource import ai_buddy_resource_policy


@event.listens_for(Session, 'do_orm_execute', propagate=True)
def inject_ai_buddy_group_visibility_filter(orm_execute_state: ORMExecuteState) -> None:
    """
    为 AI 资源查询自动追加分组可见性过滤条件

    :param orm_execute_state: ORM 执行状态
    :return:
    """
    if not orm_execute_state.is_select or orm_execute_state.is_column_load:
        return
    statement = cast('Select[Any]', orm_execute_state.statement)
    resource_models = {
        mapper.class_ for mapper in orm_execute_state.all_mappers if mapper.class_ in AI_GROUP_RESOURCE_MODEL_CLASSES
    }
    if not resource_models:
        resource_models = get_statement_ai_buddy_resource_models(statement)
    if not resource_models:
        return
    user_id = ctx.user_id
    is_superuser = ctx.is_superuser
    if user_id is None or is_superuser:
        return
    orm_execute_state.statement = apply_ai_buddy_group_visibility_criteria(
        statement,
        user_id=user_id,
        resource_models=resource_models,
        is_superuser=is_superuser,
    )


def setup(app: FastAPI) -> None:
    """
    注册 AI 分组资源调用策略

    :param app: FastAPI 应用
    :return:
    """
    register_ai_buddy_resource_policy(ai_buddy_resource_policy)
