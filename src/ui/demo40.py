import uuid
import streamlit as st
import pandas as pd
import plotly.express as px
from agent import data_agent
from utils.cache import CacheType, global_cache
from utils.common_util import render_user_message

st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀数据与消息分离的简易Demo")


def chart_bar_plotly(id: str, data: list[dict]):
    df = pd.DataFrame(data, columns=data[0].keys())
    # 指定坐标系
    df_melted = df.melt(id_vars="国家", var_name="奖牌", value_name="奖牌数")
    custom_colors = {
        "中国": "#FF0000",  # 红色
        "美国": "#002868",  # 蓝色
        "英国": "#FFA500"   # 橙色
    }
    fig = px.bar(
        df_melted, 
        x="奖牌", 
        y="奖牌数", 
        color="国家", 
        barmode="group",
        title="各国奖牌分布图",
        color_discrete_map=custom_colors,
        category_orders={"奖牌": ["金牌", "银牌", "铜牌"]},  # 确保顺序正确
        text_auto=True,  # 自动显示数值
    )

    st.plotly_chart(fig, key=id)
    with st.expander("查看当前数据详情"):
        idx = f"table_{id}"
        st.dataframe(df, key=idx)


def render_assistant_message(content: list[str], data_meta: dict):
    for item in content:
        st.markdown(item)
    
    data = None
    if data_meta and data_meta.store_type == "local":
        st.markdown("#### 本地图表")
        store_key = str(uuid.uuid4())
        data = data_meta.data
    elif data_meta and data_meta.store_type == "memory":
        st.markdown("#### 内存图表")
        store_key = data_meta.store_key
        key = f"{CacheType.KEY_PAYLOAD_DATA}:{store_key}"
        data = global_cache.get(key, CacheType.HOT)
    
    if data:
        chart_bar_plotly(store_key, data)


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": {"text": ["请输入问题，我会尽力回答。"], "data_meta": {}}}]


for msg in st.session_state.messages:
    if msg["role"] == "user" or msg["role"] == "human":
        render_user_message(msg["content"])
    else:
        with st.chat_message("assistant"):
            render_assistant_message(msg["content"].get("text", []), msg["content"].get("data_meta", {}))


if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user_message(prompt)

    with st.chat_message("assistant"):
        for state in data_agent.graph2.stream({"messages": prompt}):
            for key, value in state.items():
                #print(f"{key}: {value}")
                messages = value.get("messages", [])
                data_meta = value.get("data_meta", {})
                contents = []
                for message in messages:
                    raw_content = getattr(message, "content", message.get("content") if isinstance(message, dict) else "")
                    contents.append(raw_content)
                render_assistant_message(contents, data_meta)
                st.session_state.messages.append({"role": "assistant", "content": {"text": contents, "data_meta": data_meta}})
