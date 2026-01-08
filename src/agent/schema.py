from enum import StrEnum
from typing import Any
from dataclasses import dataclass, field

from langgraph.graph import MessagesState


class DisplayType(StrEnum):
    """数据协议类型枚举"""
    TABLE = "table"
    JSON = "json"
    CHART = "chart"
    MARKDOWN = "markdown"
    TEXT = "text"
    IMAGE = "image"
    LIVE = "live"
    VIDEO = "video"
    PENDING = "pending"
    ERROR = "error"

@dataclass
class DataMetaProtocol:
    """数据元信息协议类"""
    store_type: str # 存储类型 local、memory、redis、mysql等
    store_key: str # 存储键，用于唯一标识数据
    row_count: int # 数据行数
    data: list[dict[str, Any]] = field(default_factory=list) # 数据内容


class CustomState(MessagesState):
    """自定义状态"""
    type: DisplayType # 数据类型
    data_meta: DataMetaProtocol # 数据元信息