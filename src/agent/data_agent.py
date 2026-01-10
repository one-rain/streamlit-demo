from dataclasses import asdict
import json
import os
import uuid

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END

from agent.schema import CustomState, DataMetaProtocol
from utils.cache import CacheType, global_cache


def node_start(state: CustomState):
    print("node start...")
    question = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"你的问题是：{question}")]}

def call_model(state: CustomState):
    print("start call model...")

    # 项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    medal_list = json.load(open(os.path.join(root_dir, "data/medal_list1.json"), "r", encoding="utf-8"))
    store_key = str(uuid.uuid4())
    
    # 随机判断store_key的奇偶性
    is_even = hash(store_key) % 2 == 0
    if is_even:
        print(f"表格数据已发送到前端本地")
        data_meta = DataMetaProtocol(store_key=store_key, store_type="local", row_count=len(medal_list), data=medal_list)
    else:
        print(f"表格数据已发送到前端内存")
        key = f"{CacheType.KEY_PAYLOAD_DATA}:{store_key}"
        global_cache.set(key, medal_list, CacheType.HOT)
        data_meta = DataMetaProtocol(store_key=store_key, store_type="memory", row_count=len(medal_list))
    
    return {"messages": [AIMessage(content="已经完成表格的提取。")], "data_meta": data_meta}


graph2 = StateGraph(MessagesState)
graph2.add_node("start", node_start)
graph2.add_node("model", call_model)
graph2.add_edge(START, "start")
graph2.add_edge("start", "model")
graph2.add_edge("model", END)
graph2 = graph2.compile()
