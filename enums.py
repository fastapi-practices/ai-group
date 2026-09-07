from backend.common.enums import IntEnum


class AIBuddyResourceType(IntEnum):
    """AI 分组资源类型"""

    provider = 0
    model = 1
    mcp = 2


class AIBuddyResourceScopeType(IntEnum):
    """AI 分组资源范围类型"""

    all = 0
    none = 1
    specified = 2
