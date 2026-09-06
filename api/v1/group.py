from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.ai_buddy_group.schema.group import (
    AIGroupUserIdsParam,
    CreateAIGroupParam,
    DeleteAIGroupParam,
    GetAIGroupDetail,
    GetAIGroupUserDetail,
    GetAIGroupWithResourceDetail,
    UpdateAIGroupParam,
    UpdateAIGroupResourceParam,
)
from backend.plugin.ai_buddy_group.service.group_service import ai_group_service

router = APIRouter()


@router.get('/all', summary='获取所有 AI 分组', dependencies=[DependsJwtAuth])
async def get_all_ai_groups(db: CurrentSession) -> ResponseSchemaModel[list[GetAIGroupDetail]]:
    data = await ai_group_service.get_all(db=db)
    return response_base.success(data=data)


@router.get('/users/{user_id}', summary='获取用户所属 AI 分组', dependencies=[DependsJwtAuth])
async def get_user_ai_groups(
    db: CurrentSession,
    user_id: Annotated[int, Path(description='用户 ID')],
) -> ResponseSchemaModel[list[GetAIGroupDetail]]:
    data = await ai_group_service.get_user_groups(db=db, user_id=user_id)
    return response_base.success(data=data)


@router.get('/{pk}', summary='获取 AI 分组详情', dependencies=[DependsJwtAuth])
async def get_ai_group(
    db: CurrentSession,
    pk: Annotated[int, Path(description='分组 ID')],
) -> ResponseSchemaModel[GetAIGroupWithResourceDetail]:
    data = await ai_group_service.get(db=db, pk=pk)
    return response_base.success(data=data)


@router.get(
    '',
    summary='分页获取所有 AI 分组',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_ai_groups_paginated(
    db: CurrentSession,
    name: Annotated[str | None, Query(description='分组名称')] = None,
) -> ResponseSchemaModel[PageData[GetAIGroupDetail]]:
    page_data = await ai_group_service.get_list(db=db, name=name)
    return response_base.success(data=page_data)


@router.get('/{pk}/users', summary='获取 AI 分组用户', dependencies=[DependsJwtAuth])
async def get_ai_group_users(
    db: CurrentSession,
    pk: Annotated[int, Path(description='分组 ID')],
) -> ResponseSchemaModel[list[GetAIGroupUserDetail]]:
    data = await ai_group_service.get_group_users(db=db, pk=pk)
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建 AI 分组',
    dependencies=[
        Depends(RequestPermission('ai:group:add')),
        DependsRBAC,
    ],
)
async def create_ai_group(db: CurrentSessionTransaction, obj: CreateAIGroupParam) -> ResponseModel:
    await ai_group_service.create(db=db, obj=obj)
    return response_base.success()


@router.post(
    '/{pk}/users',
    summary='绑定 AI 分组用户',
    dependencies=[
        Depends(RequestPermission('ai:group:edit')),
        DependsRBAC,
    ],
)
async def bind_ai_group_users(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='分组 ID')],
    obj: AIGroupUserIdsParam,
) -> ResponseModel:
    await ai_group_service.bind_users(db=db, pk=pk, obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新 AI 分组',
    dependencies=[
        Depends(RequestPermission('ai:group:edit')),
        DependsRBAC,
    ],
)
async def update_ai_group(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='分组 ID')],
    obj: UpdateAIGroupParam,
) -> ResponseModel:
    count = await ai_group_service.update(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{pk}/resources',
    summary='更新 AI 分组资源',
    dependencies=[
        Depends(RequestPermission('ai:group:edit')),
        DependsRBAC,
    ],
)
async def update_ai_group_resources(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='分组 ID')],
    obj: UpdateAIGroupResourceParam,
) -> ResponseModel:
    count = await ai_group_service.update_resources(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{pk}/users',
    summary='移除 AI 分组用户',
    dependencies=[
        Depends(RequestPermission('ai:group:edit')),
        DependsRBAC,
    ],
)
async def unbind_ai_group_users(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='分组 ID')],
    obj: AIGroupUserIdsParam,
) -> ResponseModel:
    count = await ai_group_service.unbind_users(db=db, pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除 AI 分组',
    dependencies=[
        Depends(RequestPermission('ai:group:del')),
        DependsRBAC,
    ],
)
async def delete_ai_groups(db: CurrentSessionTransaction, obj: DeleteAIGroupParam) -> ResponseModel:
    count = await ai_group_service.delete(db=db, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
