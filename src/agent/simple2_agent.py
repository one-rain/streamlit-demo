import json
import os
import uuid

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END


def node_start(state: MessagesState):
    print("node start...")
    question = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"你的问题是：{question}")]}

def call_model(state: MessagesState):
    print("start call model...")

    # 项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    medal_list = json.load(open(os.path.join(root_dir, "data/medal_list2.json"), "r", encoding="utf-8"))
    data_meta = {"id": str(uuid.uuid4()), "data": medal_list}
    return {"messages": [AIMessage(content="获取到数据, 如下："), AIMessage(content=json.dumps(data_meta, ensure_ascii=False))]}


graph1 = StateGraph(MessagesState)
graph1.add_node("start", node_start)
graph1.add_node("model", call_model)
graph1.add_edge(START, "start")
graph1.add_edge("start", "model")
graph1.add_edge("model", END)
graph1 = graph1.compile()
