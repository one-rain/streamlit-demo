import json

from vega_datasets import data
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END


column_mapping = {
    'yield': '产量',
    'variety': '品种',
    'year': '年份',
    'site': '地区',
}


def node_start(state: MessagesState):
    print("node start...")
    question = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"你的问题是：{question}")]}

def call_model(state: MessagesState):
    print("start call model...")

    barley = data.barley()
    filtered_df = barley[barley["year"] == 1931]
    data_json = filtered_df.to_dict(orient="records")

    return {"messages": [AIMessage(content="获取到数据, 如下："), AIMessage(content=json.dumps(data_json, ensure_ascii=False))]}


def build_graph():
    graph1 = StateGraph(MessagesState)
    graph1.add_node("start", node_start)
    graph1.add_node("model", call_model)
    graph1.add_edge(START, "start")
    graph1.add_edge("start", "model")
    graph1.add_edge("model", END)
    return graph1.compile()