import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class AIBuddyResource(Base):
    """AI 分组资源表"""

    __tablename__ = 'ai_buddy_resource'
    __table_args__ = (
        sa.UniqueConstraint(
            'group_id',
            'resource_type',
            'scope_type',
            'resource_id',
            'deleted',
            name='uk_ai_buddy_resource_group_type_scope_resource_deleted',
        ),
        {'comment': 'AI 分组资源'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    group_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='分组 ID')
    resource_type: Mapped[int] = mapped_column(index=True, comment='资源类型（0服务商 1模型 2MCP）')
    scope_type: Mapped[int] = mapped_column(default=0, index=True, comment='范围类型（0全部 1无 2指定）')
    resource_id: Mapped[int] = mapped_column(sa.BigInteger, default=0, index=True, comment='资源 ID')
