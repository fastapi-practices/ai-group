from datetime import datetime

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class AIBuddyGroupSchemaBase(SchemaBase):
    """AI 分组基础模型"""

    name: str = Field(description='分组名称')
    description: str | None = Field(None, description='分组描述')


class CreateAIBuddyGroupParam(AIBuddyGroupSchemaBase):
    """创建 AI 分组参数"""


class UpdateAIBuddyGroupParam(SchemaBase):
    """更新 AI 分组参数"""

    name: str | None = Field(None, description='分组名称')
    description: str | None = Field(None, description='分组描述')


class UpdateAIBuddyResourceParam(SchemaBase):
    """更新 AI 分组资源参数"""

    provider_ids: list[int] | None = Field(
        None,
        description='可见服务商 ID 列表，None 表示全部可见，空列表表示全部不可见',
    )
    model_ids: list[int] | None = Field(None, description='可见模型 ID 列表，None 表示全部可见，空列表表示全部不可见')
    mcp_ids: list[int] | None = Field(None, description='可见 MCP ID 列表，None 表示全部可见，空列表表示全部不可见')


class AIBuddyUserIdsParam(SchemaBase):
    """AI 分组用户 ID 参数"""

    user_ids: list[int] = Field(description='用户 ID 列表')


class DeleteAIBuddyGroupParam(SchemaBase):
    """批量删除 AI 分组参数"""

    pks: list[int] = Field(description='分组 ID 列表')


class GetAIBuddyGroupDetail(AIBuddyGroupSchemaBase):
    """AI 分组详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='分组 ID')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(None, description='更新时间')


class GetAIBuddyGroupWithResourceDetail(GetAIBuddyGroupDetail):
    """AI 分组资源详情"""

    provider_ids: list[int] | None = Field(
        None,
        description='可见服务商 ID 列表，None 表示全部可见，空列表表示全部不可见',
    )
    model_ids: list[int] | None = Field(None, description='可见模型 ID 列表，None 表示全部可见，空列表表示全部不可见')
    mcp_ids: list[int] | None = Field(None, description='可见 MCP ID 列表，None 表示全部可见，空列表表示全部不可见')


class GetAIBuddyUserDetail(SchemaBase):
    """AI 分组用户详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='分组用户 ID')
    group_id: int = Field(description='分组 ID')
    user_id: int = Field(description='用户 ID')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(None, description='更新时间')
