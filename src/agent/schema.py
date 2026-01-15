from cProfile import label
from enum import StrEnum
from typing import Any

from langgraph.graph import MessagesState
from pydantic import BaseModel, model_validator


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

class ChartType(StrEnum):
    """图表类型枚举"""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    TABLE = "table"


class DataMetaSpec(BaseModel):
    """数据元信息协议类"""
    store_type: str # 存储类型 local、memory等
    store_key: str # 存储键，用于唯一标识数据
    row_count: int # 数据行数
    data: list[Any] = [] # 数据内容
    display_type: DisplayType = DisplayType.TABLE # 显示类型


class DataFieldSchema(BaseModel):
    """数据字段协议类"""
    name: str # 列名
    category: str # 列分类 dimension、metric
    title: str = None # 列标题，默认与name相同
    type: str = None # 列类型, 可选值为"string"、"int"、"float"、"date"、"datetime"等
    format: str = None # 列格式, 可选值为"%Y-%m-%d"等
    aggregate: str = None # 聚合函数, sum、avg、count等
    display: bool = True # 是否显示该列

    @model_validator(mode="after")
    def _fill_default_title(self):
        if not self.title:
            self.title = self.name
        return self


class ChartOption(BaseModel):
    """图表筛选选项协议类"""
    label: str = None # 选项标签
    values: list[Any] # 选项值列表

class ChartMapping(BaseModel):
    """图表映射协议类"""
    x_axis: str # x轴列名
    y_axis: str # 默认的y轴列名
    series: list[str] | dict[str, Any] = None # 系列列名
    dim_options: list[dict[str, Any]] = None # 维度筛选项，元素为ChartOption
    metric_option: dict[str, Any] = None # 指标筛选项，元素为ChartOption

class DataSet(BaseModel):
    """图表数据集协议类。数据格式默认采用宽格式，即每一行数据都是一个样本，每个样本的每个特征都有一个值。"""
    id: str # 数据集ID，用于唯一标识数据集
    field_schemas: list[dict[str, Any]] = [] # 数据字段协议列表，每个元素为一个字典，对应DataFieldSchema协议
    data: list[dict[str, Any]] = [] # 数据内容，格式：[{"列名": 列值1}, {"列名": 列值2}, ...]
    format: str = "wide" # 数据格式, 可选值为"wide"、"long"

class ChartSpec(BaseModel):
    """图表数据协议类"""
    chart_type: ChartType # 图表类型, 可选值为ChartType枚举
    title: str = "" # 数据相关主题，用于图表标题
    dataset: dict[str, Any] = {} # 图表数据集, 对应DataSet协议
    mapping: dict[str, Any] = {} # 图表映射, 对应ChartMapping协议

class CustomState(MessagesState):
    """自定义状态"""
    data_meta: dict[str, Any] # 数据元信息，对应DataMetaProtocol


class CustomChartState(MessagesState):
    """自定义图表状态"""
    chart_spec: dict[str, Any] = {} # 图表规格, 对应ChartSpec协议
