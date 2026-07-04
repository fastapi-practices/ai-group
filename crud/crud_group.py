from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.ai_group.model import AIGroup
from backend.plugin.ai_group.schema.group import CreateAIGroupParam
from backend.utils.timezone import timezone


class CRUDAIGroup(CRUDPlus[AIGroup]):
    """AI 分组数据库操作类"""

    async def get(self, db: AsyncSession, pk: int) -> AIGroup | None:
        """
        获取分组

        :param db: 数据库会话
        :param pk: 分组 ID
        :return:
        """
        return await self.select_model(db, pk, deleted=0)

    async def get_by_ids(self, db: AsyncSession, pks: list[int]) -> Sequence[AIGroup]:
        """
        批量获取分组

        :param db: 数据库会话
        :param pks: 分组 ID 列表
        :return:
        """
        return await self.select_models(db, id__in=pks, deleted=0)

    async def get_by_name(self, db: AsyncSession, name: str) -> AIGroup | None:
        """
        通过名称获取分组

        :param db: 数据库会话
        :param name: 分组名称
        :return:
        """
        return await self.select_model_by_column(db, name=name, deleted=0)

    async def get_select(self, name: str | None) -> Select:
        """
        获取分组列表查询表达式

        :param name: 分组名称
        :return:
        """
        filters = {'deleted': 0}
        if name is not None:
            filters['name__like'] = f'%{name}%'
        return await self.select_order('id', 'desc', **filters)

    async def get_all(self, db: AsyncSession) -> Sequence[AIGroup]:
        """
        获取所有分组

        :param db: 数据库会话
        :return:
        """
        return await self.select_models_order(db, 'id', 'desc', deleted=0)

    async def create(self, db: AsyncSession, obj: CreateAIGroupParam) -> AIGroup:
        """
        创建分组

        :param db: 数据库会话
        :param obj: 创建分组参数
        :return:
        """
        return await self.create_model(db, obj, flush=True)

    async def update(self, db: AsyncSession, pk: int, obj: dict[str, Any]) -> int:
        """
        更新分组

        :param db: 数据库会话
        :param pk: 分组 ID
        :param obj: 更新分组参数
        :return:
        """
        return await self.update_model_by_column(db, obj, id=pk, deleted=0)

    async def delete(self, db: AsyncSession, pks: list[int]) -> int:
        """
        批量删除分组

        :param db: 数据库会话
        :param pks: 分组 ID 列表
        :return:
        """
        return await self.delete_model_by_column(
            db,
            allow_multiple=True,
            logical_deletion=True,
            deleted_flag_column='deleted',
            deleted_flag_value=self.model.id,
            deleted_at_column='deleted_time',
            deleted_at_factory=timezone.now(),
            id__in=pks,
            deleted=0,
        )


ai_group_dao: CRUDAIGroup = CRUDAIGroup(AIGroup)
