from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.ai_group.model import AIGroupResource
from backend.utils.timezone import timezone


class CRUDAIGroupResource(CRUDPlus[AIGroupResource]):
    """AI 分组资源数据库操作类"""

    async def get_by_group_id(self, db: AsyncSession, group_id: int) -> Sequence[AIGroupResource]:
        """
        获取分组资源

        :param db: 数据库会话
        :param group_id: 分组 ID
        :return:
        """
        return await self.select_models(db, group_id=group_id, deleted=0)

    async def get_by_group_ids(self, db: AsyncSession, group_ids: list[int]) -> Sequence[AIGroupResource]:
        """
        批量获取分组资源

        :param db: 数据库会话
        :param group_ids: 分组 ID 列表
        :return:
        """
        return await self.select_models(db, group_id__in=group_ids, deleted=0)

    async def bulk_create(self, db: AsyncSession, objs: list[dict[str, Any]]) -> int:
        """
        批量创建分组资源

        :param db: 数据库会话
        :param objs: 分组资源列表
        :return:
        """
        now = timezone.now()
        await self.bulk_create_models(db, [{**obj, 'created_time': now} for obj in objs])
        return len(objs)

    async def delete_by_group_id(self, db: AsyncSession, group_id: int) -> int:
        """
        删除分组资源

        :param db: 数据库会话
        :param group_id: 分组 ID
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
            group_id=group_id,
            deleted=0,
        )

    async def delete_by_group_ids(self, db: AsyncSession, group_ids: list[int]) -> int:
        """
        批量删除分组资源

        :param db: 数据库会话
        :param group_ids: 分组 ID 列表
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
            group_id__in=group_ids,
            deleted=0,
        )


ai_group_resource_dao: CRUDAIGroupResource = CRUDAIGroupResource(AIGroupResource)
