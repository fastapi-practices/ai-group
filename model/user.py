import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class AIGroupUser(Base):
    """AI 分组用户"""

    __tablename__ = 'ai_group_user'
    __table_args__ = (
        sa.UniqueConstraint('group_id', 'user_id', 'deleted', name='uk_ai_group_user_group_user_deleted'),
        {'comment': 'AI 分组用户'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    group_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='分组 ID')
    user_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='用户 ID')
