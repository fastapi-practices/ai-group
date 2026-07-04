from collections.abc import Sequence
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.admin.model import User
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.plugin.ai.model import AIModel, AIProvider, Mcp
from backend.plugin.ai_group.crud.crud_group import ai_group_dao
from backend.plugin.ai_group.crud.crud_resource import ai_group_resource_dao
from backend.plugin.ai_group.crud.crud_user import ai_group_user_dao
from backend.plugin.ai_group.enums import AIGroupResourceScopeType, AIGroupResourceType
from backend.plugin.ai_group.model import AIGroup
from backend.plugin.ai_group.schema.group import (
    AIGroupUserIdsParam,
    CreateAIGroupParam,
    DeleteAIGroupParam,
    GetAIGroupDetail,
    GetAIGroupUserDetail,
    GetAIGroupWithResourceDetail,
    UpdateAIGroupParam,
    UpdateAIGroupResourceParam,
)


class AIGroupService:
    """AI 分组服务类"""

    @staticmethod
    async def _validate_user_ids(*, db: AsyncSession, user_ids: list[int]) -> None:
        """校验指定用户是否存在"""
        if not user_ids:
            raise errors.RequestError(msg='用户 ID 列表不能为空')
        stmt = select(func.count()).select_from(User).where(User.id.in_(user_ids), User.deleted == 0)
        count = (await db.execute(stmt)).scalar_one()
        if count != len(user_ids):
            raise errors.NotFoundError(msg='用户不存在')

    @staticmethod
    async def get_all(*, db: AsyncSession) -> Sequence[AIGroup]:
        """
        获取所有分组

        :param db: 数据库会话
        :return:
        """
        return await ai_group_dao.get_all(db)

    @staticmethod
    async def get(*, db: AsyncSession, pk: int) -> GetAIGroupWithResourceDetail:
        """
        获取分组详情

        :param db: 数据库会话
        :param pk: 分组 ID
        :return:
        """
        ai_group = await ai_group_dao.get(db, pk)
        if not ai_group:
            raise errors.NotFoundError(msg='分组不存在')
        resources = await ai_group_resource_dao.get_by_group_id(db, pk)
        resource_ids = {'provider_ids': None, 'model_ids': None, 'mcp_ids': None}
        for resource in resources:
            field = f'{AIGroupResourceType(resource.resource_type).name}_ids'
            scope_type = AIGroupResourceScopeType(resource.scope_type)
            if scope_type == AIGroupResourceScopeType.none:
                resource_ids[field] = []
            elif scope_type == AIGroupResourceScopeType.specified:
                resource_ids[field] = resource_ids[field] or []
                resource_ids[field].append(resource.resource_id)
        data = GetAIGroupDetail.model_validate(ai_group).model_dump()
        data.update(resource_ids)
        return GetAIGroupWithResourceDetail(**data)

    @staticmethod
    async def get_list(*, db: AsyncSession, name: str | None) -> dict[str, Any]:
        """
        获取分组列表

        :param db: 数据库会话
        :param name: 分组名称
        :return:
        """
        ai_group_select = await ai_group_dao.get_select(name)
        return await paging_data(db, ai_group_select)

    @staticmethod
    async def get_user_groups(*, db: AsyncSession, user_id: int) -> Sequence[AIGroup]:
        """
        获取用户所属分组

        :param db: 数据库会话
        :param user_id: 用户 ID
        :return:
        """
        await AIGroupService._validate_user_ids(db=db, user_ids=[user_id])
        group_ids = await ai_group_user_dao.get_group_ids_by_user(db, user_id)
        return await ai_group_dao.get_by_ids(db, group_ids)

    @staticmethod
    async def get_group_users(*, db: AsyncSession, pk: int) -> list[GetAIGroupUserDetail]:
        """
        获取分组用户

        :param db: 数据库会话
        :param pk: 分组 ID
        :return:
        """
        ai_group = await ai_group_dao.get(db, pk)
        if not ai_group:
            raise errors.NotFoundError(msg='分组不存在')
        users = await ai_group_user_dao.get_by_group_id(db, pk)
        return [GetAIGroupUserDetail.model_validate(user) for user in users]

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAIGroupParam) -> None:
        """
        创建分组

        :param db: 数据库会话
        :param obj: 创建分组参数
        :return:
        """
        payload = obj.model_dump(mode='json')
        name = payload['name'].strip()
        if not name:
            raise errors.RequestError(msg='分组名称不能为空')
        description = payload['description'].strip() if payload['description'] else None
        payload.update(name=name, description=description)
        if await ai_group_dao.get_by_name(db, payload['name']):
            raise errors.ConflictError(msg='分组已存在')
        ai_group = await ai_group_dao.create(db, CreateAIGroupParam(**payload))
        await ai_group_resource_dao.bulk_create(
            db,
            [
                {
                    'group_id': ai_group.id,
                    'resource_type': AIGroupResourceType.provider.value,
                    'scope_type': AIGroupResourceScopeType.all.value,
                    'resource_id': 0,
                },
                {
                    'group_id': ai_group.id,
                    'resource_type': AIGroupResourceType.model.value,
                    'scope_type': AIGroupResourceScopeType.all.value,
                    'resource_id': 0,
                },
                {
                    'group_id': ai_group.id,
                    'resource_type': AIGroupResourceType.mcp.value,
                    'scope_type': AIGroupResourceScopeType.all.value,
                    'resource_id': 0,
                },
            ],
        )

    @staticmethod
    async def update(*, db: AsyncSession, pk: int, obj: UpdateAIGroupParam) -> int:
        """
        更新分组

        :param db: 数据库会话
        :param pk: 分组 ID
        :param obj: 更新分组参数
        :return:
        """
        ai_group = await ai_group_dao.get(db, pk)
        if not ai_group:
            raise errors.NotFoundError(msg='分组不存在')
        payload = obj.model_dump(mode='json', exclude_unset=True)
        if 'name' in payload:
            name = payload['name'].strip() if payload['name'] else ''
            if not name:
                raise errors.RequestError(msg='分组名称不能为空')
            payload['name'] = name
        if 'description' in payload:
            payload['description'] = payload['description'].strip() if payload['description'] else None
        if not payload:
            raise errors.RequestError(msg='更新内容不能为空')
        name = payload.get('name')
        if name is not None and ai_group.name != name and await ai_group_dao.get_by_name(db, name):
            raise errors.ConflictError(msg='分组已存在')
        return await ai_group_dao.update(db, pk, payload)

    @staticmethod
    async def update_resources(*, db: AsyncSession, pk: int, obj: UpdateAIGroupResourceParam) -> int:
        """
        更新分组资源

        :param db: 数据库会话
        :param pk: 分组 ID
        :param obj: 更新分组资源参数
        :return:
        """
        ai_group = await ai_group_dao.get(db, pk)
        if not ai_group:
            raise errors.NotFoundError(msg='分组不存在')

        provider_ids = None if obj.provider_ids is None else list(dict.fromkeys(obj.provider_ids))
        model_ids = None if obj.model_ids is None else list(dict.fromkeys(obj.model_ids))
        mcp_ids = None if obj.mcp_ids is None else list(dict.fromkeys(obj.mcp_ids))
        for resource_ids, model, error_msg in (
            (provider_ids, AIProvider, '服务商不存在'),
            (model_ids, AIModel, '模型不存在'),
            (mcp_ids, Mcp, 'MCP不存在'),
        ):
            if not resource_ids:
                continue
            stmt = select(func.count()).select_from(model).where(model.id.in_(resource_ids), model.deleted == 0)
            resource_count = (await db.execute(stmt)).scalar_one()
            if resource_count != len(resource_ids):
                raise errors.NotFoundError(msg=error_msg)

        await ai_group_resource_dao.delete_by_group_id(db, pk)
        resource_payloads = []
        for resource_type, resource_ids in (
            (AIGroupResourceType.provider, provider_ids),
            (AIGroupResourceType.model, model_ids),
            (AIGroupResourceType.mcp, mcp_ids),
        ):
            if resource_ids is None:
                resource_payloads.append({
                    'group_id': pk,
                    'resource_type': resource_type.value,
                    'scope_type': AIGroupResourceScopeType.all.value,
                    'resource_id': 0,
                })
            elif not resource_ids:
                resource_payloads.append({
                    'group_id': pk,
                    'resource_type': resource_type.value,
                    'scope_type': AIGroupResourceScopeType.none.value,
                    'resource_id': 0,
                })
            else:
                resource_payloads.extend(
                    {
                        'group_id': pk,
                        'resource_type': resource_type.value,
                        'scope_type': AIGroupResourceScopeType.specified.value,
                        'resource_id': resource_id,
                    }
                    for resource_id in resource_ids
                )
        return await ai_group_resource_dao.bulk_create(db, resource_payloads)

    @staticmethod
    async def bind_users(*, db: AsyncSession, pk: int, obj: AIGroupUserIdsParam) -> None:
        """
        绑定分组用户

        :param db: 数据库会话
        :param pk: 分组 ID
        :param obj: 用户 ID 列表
        :return:
        """
        ai_group = await ai_group_dao.get(db, pk)
        if not ai_group:
            raise errors.NotFoundError(msg='分组不存在')
        user_ids = list(dict.fromkeys(obj.user_ids))
        await AIGroupService._validate_user_ids(db=db, user_ids=user_ids)
        existing_users = await ai_group_user_dao.get_by_group_and_users(db, pk, user_ids)
        if existing_users:
            raise errors.ConflictError(msg='用户已绑定此分组')
        await ai_group_user_dao.bulk_create(
            db,
            [{'group_id': pk, 'user_id': user_id} for user_id in user_ids],
        )

    @staticmethod
    async def unbind_users(*, db: AsyncSession, pk: int, obj: AIGroupUserIdsParam) -> int:
        """
        移除分组用户

        :param db: 数据库会话
        :param pk: 分组 ID
        :param obj: 用户 ID 列表
        :return:
        """
        ai_group = await ai_group_dao.get(db, pk)
        if not ai_group:
            raise errors.NotFoundError(msg='分组不存在')
        user_ids = list(dict.fromkeys(obj.user_ids))
        if not user_ids:
            raise errors.RequestError(msg='用户 ID 列表不能为空')
        return await ai_group_user_dao.delete_by_group_and_users(db, pk, user_ids)

    @staticmethod
    async def delete(*, db: AsyncSession, obj: DeleteAIGroupParam) -> int:
        """
        批量删除分组

        :param db: 数据库会话
        :param obj: 分组 ID 列表
        :return:
        """
        await ai_group_user_dao.delete_by_group_ids(db, obj.pks)
        await ai_group_resource_dao.delete_by_group_ids(db, obj.pks)
        return await ai_group_dao.delete(db, obj.pks)


ai_group_service: AIGroupService = AIGroupService()
