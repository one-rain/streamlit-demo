import json
import os
import random
import time
from langchain.chat_models import init_chat_model

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END

from agent.schema import ChartMapping, ChartOption, ChartSpec, ChartType, CustomChartState, DataFieldSchema, DataSet

model = init_chat_model(model_provider="openai", base_url="http://127.0.0.1:1234/v1", api_key="not-needed", model="qwen/qwen3-8b", verbose=True)


def node_start(state: CustomChartState):
    print("node start...")
    question = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"你的问题是：{question}")]}

def call_model(state: CustomChartState):
    print("start call model...")

    # 项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dau_list = json.load(open(os.path.join(root_dir, "data/app_dau.json"), "r", encoding="utf-8"))

    field_schemas = [
        DataFieldSchema(name="date", category="dimension", title="日期", type="date", format="%Y-%m-%d").model_dump(exclude_none=True),
        DataFieldSchema(name="company", category="dimension", title="公司", type="string").model_dump(exclude_none=True),
        DataFieldSchema(name="name", category="dimension", title="应用", type="string").model_dump(exclude_none=True),
        DataFieldSchema(name="dau", category="metric", title="DAU", type="int", aggregate="count").model_dump(exclude_none=True),
        DataFieldSchema(name="dnu", category="metric", title="DNU", type="int", aggregate="count", display=False).model_dump(exclude_none=True),
    ]

    # 时间戳当作id
    time_num = int(time.time())
    dataset = DataSet(
        id=f"dau-{time_num}",
        field_schemas=field_schemas,
        data=dau_list,
        format="wide",
    )

    mapping = ChartMapping(
        x_axis="日期", 
        y_axis="DAU", 
        series=["公司"],
        dim_options=[ChartOption(label="应用", values=["app1", "app2"]).model_dump(exclude_none=True)],
        metric_option=ChartOption(label="指标", values=["DAU", "DNU"]).model_dump(exclude_none=True),
    ).model_dump(exclude_none=True)

    # 从3个chart_type中随机选择一个类型
    chart_type = random.choice([ChartType.PIE.value, ChartType.BAR.value, ChartType.LINE.value])

    chart_spec = ChartSpec(
        chart_type=chart_type,
        title="各公司DAU/DNU趋势", 
        dataset=dataset.model_dump(), 
        mapping=mapping
    )

    # TODO: ChartSpec的信息可以通过llm生成

    return {"messages": [AIMessage(content="✅ 已经完成数据的提取。")], "chart_spec": chart_spec.model_dump()}


def build_chart_graph():
    graph = StateGraph(MessagesState)
    graph.add_node("start", node_start)
    graph.add_node("model", call_model)
    graph.add_edge(START, "start")
    graph.add_edge("start", "model")
    graph.add_edge("model", END)
    graph = graph.compile()
    return graph
