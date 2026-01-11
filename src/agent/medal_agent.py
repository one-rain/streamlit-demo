import json
import os
import uuid

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.state import RunnableConfig

from agent.schema import CustomState, DataMetaProtocol
from utils.cache import CacheType, global_cache


def node_start(state: CustomState):
    print("node start...")
    question = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"你的问题是：{question}")]}

def call_model(state: CustomState, config: RunnableConfig):
    print("start call model...")

    data_type = config.get("configurable", {}).get("data_type", "medal_width")
    store_type = config.get("configurable", {}).get("store_type", "")
    file_name = "medal_width.json"
    if data_type == "medal_long":
        file_name = "medal_long.json"

    # 项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    medal_list = json.load(open(os.path.join(root_dir, f"data/{file_name}"), "r", encoding="utf-8"))
    store_key = str(uuid.uuid4())
    # 随机判断store_key的奇偶性
    is_even = hash(store_key) % 2 == 0
    if store_type == "local" or is_even:
        print(f"表格数据已发送到前端本地")
        data_meta = DataMetaProtocol(store_key=store_key, store_type="local", row_count=len(medal_list), data=medal_list)
    else:
        print(f"表格数据已发送到前端内存") # 模拟重新请求获取数据
        key = f"{CacheType.KEY_PAYLOAD_DATA}:{store_key}"
        global_cache.set(key, medal_list, CacheType.HOT)
        data_meta = DataMetaProtocol(store_key=store_key, store_type="memory", row_count=len(medal_list))
    
    return {"messages": [AIMessage(content="已经完成表格的提取。")], "data_meta": data_meta.__dict__}

def build_graph():
    graph = StateGraph(CustomState)
    graph.add_node("start", node_start)
    graph.add_node("model", call_model)
    graph.add_edge(START, "start")
    graph.add_edge("start", "model")
    graph.add_edge("model", END)
    return graph.compile()
