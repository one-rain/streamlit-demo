import json
import os
import uuid
import pandas as pd
import numpy as np
import math
from dataclasses import dataclass, field, asdict
from typing import Any, List, Dict

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END


@dataclass
class DataPayload:
    chart_type: str = ""
    x: str = ""
    y: str = ""
    series: List[str] = field(default_factory=list)
    columns: List[str] = field(default_factory=list)
    data: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class DataProtocol:
    type: str = ""
    meta: dict[str, Any] = field(default_factory=dict)
    payload: DataPayload = field(default_factory=DataPayload)

def format_numbers_for_display(df: pd.DataFrame, min_precision: int = 2, max_precision: int = 10, use_thousands_sep: bool = True) -> pd.DataFrame:
    """
    将 DataFrame 中的数字格式化为字符串：
    ✅ 自动调整小数位数
    ✅ 避免科学计数法
    ✅ 可选千位分隔符
    """
    def dynamic_format(x):
        # 整数处理
        if isinstance(x, (int, np.integer)):
            return f"{x:,}" if use_thousands_sep else str(x)

        # 浮点数处理
        elif isinstance(x, (float, np.floating)):
            if np.isnan(x):
                return ""

            # 精度决策
            if x == 0:
                return "0"

            if abs(x) >= 1:
                precision = min_precision
            else:
                # 根据数量级动态增加小数位
                precision = min(
                    max_precision,
                    max(min_precision, int(-math.log10(abs(x))) + 2)
                )

            # 千位分隔符
            fmt = f"{{:,.{precision}f}}" if use_thousands_sep else f"{{:.{precision}f}}"
            out = fmt.format(x)

            # 去尾 0 和小数点
            return out.rstrip("0").rstrip(".")

        # 其它类型直接返回
        return x

    formatted_df = df.copy()

    # 只格式化非 id 字段
    def should_format(col_):
        return not (col_ == "id" or col_.endswith("_id"))

    for col in df.columns:
        if should_format(col):
            formatted_df[col] = df[col].apply(dynamic_format)

    return formatted_df

def node_start(state: MessagesState):
    print("node start...")
    question = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"你的问题是：{question}")]}

def call_model(state: MessagesState):
    print("start call model...")
    question = state["messages"][-1].content

    # 项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    medal_list = json.load(open(os.path.join(root_dir, "data/medal_list.json"), "r", encoding="utf-8"))

    if "图表" in question or "折线图" in question or "柱状图" in question:
        # 将 medal_list 转换为 图表数据格式，去掉key, 只保留value
        tmp_data = [list(item.values()) for item in medal_list]
        out_data = DataProtocol(type="chart", meta={"title": "奥运会奖牌榜"}, payload=DataPayload(chart_type="bar", x="国家", y="奖牌数", series=["金牌", "银牌", "铜牌"], columns=["国家", "金牌", "银牌", "铜牌"], data=tmp_data))
        json_data = json.dumps(asdict(out_data), ensure_ascii=False, indent=2)
        return {"messages": [AIMessage(content=json_data)]}
    elif "表格" in question:
        out_data = DataProtocol(type="table", meta={"title": "奥运会奖牌榜"}, payload=DataPayload(data=medal_list))
        json_data = json.dumps(asdict(out_data), ensure_ascii=False, indent=2)
        return {"messages": [AIMessage(content=json_data)]}
    elif "json" in question:
        out_data = DataProtocol(type="json", meta={"title": "奥运会奖牌榜"}, payload=DataPayload(data=medal_list))
        json_data = json.dumps(asdict(out_data), ensure_ascii=False, indent=2)
        return {"messages": [AIMessage(content=json_data)]}
    else: # 默认 markdown 展示
        #final_result_list = []
        #df = pd.DataFrame(medal_list, columns=["国家", "金牌", "银牌", "铜牌"])
        #df_fmt = format_numbers_for_display(df, min_precision=2, max_precision=4)
        #markdown_table = df_fmt.to_markdown(index=False)
        #final_result_list.append(f"{markdown_table}\n")
        return {"messages": [AIMessage(content=medal_list)]}

graph = StateGraph(MessagesState)
graph.add_node("start", node_start)
graph.add_node("model", call_model)
graph.add_edge(START, "start")
graph.add_edge("start", "model")
graph.add_edge("model", END)
graph = graph.compile()


if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
        }
    }

    question = "北京奥运会的开幕时间"
    state = MessagesState(messages=[HumanMessage(content=question)])

    #result_state = graph.invoke(state, config=config)
    #for message in result_state.get("messages", []):
    #    message.pretty_print()
    
    for chunk in graph.stream({"messages": [HumanMessage(content=question)]}):
        print("="*20)
        print(f"\nchunk: {chunk}\n")
