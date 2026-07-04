import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, UniversalText, id_key


class AIGroup(Base):
    """AI 分组"""

    __tablename__ = 'ai_group'
    __table_args__ = (
        sa.UniqueConstraint('name', 'deleted', name='uk_ai_group_name_deleted'),
        {'comment': 'AI 分组'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(sa.String(100), comment='分组名称')
    description: Mapped[str | None] = mapped_column(UniversalText, default=None, comment='分组描述')
