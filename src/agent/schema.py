from curses import meta
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ChartMeta:
    type: str # 图表类型，如：bar、line、pie等
    title: str # 图表标题
    x: str = ""
    y: str = ""
    series: List[str] = field(default_factory=list)
    columns: List[str] = field(default_factory=list)

@dataclass
class DataProtocol:
    type: str # 数据类型，如：table、chart、json、markdown等
    data: List[Dict[str, Any]] = field(default_factory=list)
    meta: ChartMeta = field(default_factory=ChartMeta)
