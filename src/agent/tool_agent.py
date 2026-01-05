import json
import os
import uuid
from dataclasses import asdict

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END

from agent.schema import DataPayload, DataProtocol


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
    else: # 默认展示
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
