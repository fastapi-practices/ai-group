from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.ai_buddy_group.model import AIGroupUser
from backend.utils.timezone import timezone


class CRUDAIGroupUser(CRUDPlus[AIGroupUser]):
    """AI 分组用户数据库操作类"""

    async def get_by_group_id(self, db: AsyncSession, group_id: int) -> Sequence[AIGroupUser]:
        """
        获取分组用户

        :param db: 数据库会话
        :param group_id: 分组 ID
        :return:
        """
        return await self.select_models_order(db, 'id', 'desc', group_id=group_id, deleted=0)

    async def get_group_ids_by_user(self, db: AsyncSession, user_id: int) -> list[int]:
        """
        获取用户所属分组 ID 列表

        :param db: 数据库会话
        :param user_id: 用户 ID
        :return:
        """
        rows = await self.select_models(db, user_id=user_id, deleted=0)
        return [row.group_id for row in rows]

    async def get_by_group_and_users(
        self,
        db: AsyncSession,
        group_id: int,
        user_ids: list[int],
    ) -> Sequence[AIGroupUser]:
        """
        获取分组下指定用户绑定

        :param db: 数据库会话
        :param group_id: 分组 ID
        :param user_ids: 用户 ID 列表
        :return:
        """
        return await self.select_models(db, group_id=group_id, user_id__in=user_ids, deleted=0)

    async def bulk_create(self, db: AsyncSession, objs: list[dict[str, Any]]) -> None:
        """
        批量创建分组用户

        :param db: 数据库会话
        :param objs: 分组用户列表
        :return:
        """
        now = timezone.now()
        await self.bulk_create_models(db, [{**obj, 'created_time': now} for obj in objs])

    async def delete_by_group_id(self, db: AsyncSession, group_id: int) -> int:
        """
        删除分组用户

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
        批量删除分组用户

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

    async def delete_by_group_and_users(self, db: AsyncSession, group_id: int, user_ids: list[int]) -> int:
        """
        删除分组下指定用户绑定

        :param db: 数据库会话
        :param group_id: 分组 ID
        :param user_ids: 用户 ID 列表
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
            user_id__in=user_ids,
            deleted=0,
        )


ai_group_user_dao: CRUDAIGroupUser = CRUDAIGroupUser(AIGroupUser)
