from enum import StrEnum
from typing import List, Dict, Any
from dataclasses import dataclass, field

class DataProtocolType(StrEnum):
    """数据协议类型枚举，包含：code, 说明"""
    TABLE = "table"
    JSON = "json"
    CHART = "chart"
    MARKDOWN = "markdown"
    TEXT = "text"
    IMAGES = "images"
    VIDEO = "video"

class ChartType(StrEnum):
    """图表类型枚举，包含：code, 说明"""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"


@dataclass
class ChartMeta:
    id: str # 图表ID，用于唯一标识图表
    type: ChartType # 图表类型，如：bar、line、pie等
    title: str # 图表标题
    x: str | None = None # x轴字段名
    y: str | None = None # y轴字段名
    series: List[str] = field(default_factory=list) # 系列字段名列表
    columns: List[str] = field(default_factory=list) # 列字段名列表

@dataclass
class DataProtocol:
    type: DataProtocolType # 数据类型，如：table、chart、json、text等
    data: List[Dict[str, Any]] = field(default_factory=list)
    meta: ChartMeta | None = None # 图表元数据，仅当type为chart时有效
