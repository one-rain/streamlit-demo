import html
import json
import streamlit as st
import pandas as pd
import plotly.express as px
from agent import data_agent
from utils.cache import CacheType, global_cache

st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀数据与消息分离的简易Demo")

def render_user_message(content):
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; align-items: flex-start; margin-bottom: 1rem;">
        <div style="background-color: #f0f2f6; color: #31333f; padding: 1rem; border-radius: 0.5rem; margin-right: 0.5rem; max-width: 70%; text-align: left;">
            <div style="white-space: pre-wrap;">{html.escape(content)}</div>
        </div>
        <div style="font-size: 1.5rem; line-height: 1.5;">👤</div>
    </div>
    """, unsafe_allow_html=True)

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

    st.title("各国奖牌分布图")
    st.plotly_chart(fig, key=id)
    with st.expander("查看当前数据详情"):
        idx = f"table_{id}"
        st.dataframe(df, key=idx)


def render_assistant_message(content: str | dict):
    if isinstance(content, str):
        st.markdown(content)
        return
    else:
        if content.get("type") == "text":
            st.markdown(content.get("content", ""))
        elif content.get("type") == "data":
            data_meta = content.get("content", {})
            store_type = data_meta.get("store_type", "")
            if store_type == "local":
                df = pd.DataFrame(data_meta.get("data", []))
                st.dataframe(df)
            elif store_type == "memory":
                store_key = data_meta.get("store_key", "")
                key = f"{CacheType.KEY_PAYLOAD_DATA}{store_key}"
                data = global_cache.get(key, CacheType.HOT)
                print(data)
                chart_bar_plotly(store_key, data)
            else:
                st.markdown("数据存储类型未知，无法渲染。")


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": {"type": "text", "content": "请输入问题，我会尽力回答。"}}]

for msg in st.session_state.messages:
    if msg["role"] == "user":
        render_user_message(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message(msg["role"]):
            render_assistant_message(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user_message(prompt)

    with st.chat_message("assistant"):
        for state in data_agent.graph2.stream({"messages": prompt}):
            for key, value in state.items():
                print(f"{key}: {value}")
                messages = value.get("messages", [])
                for message in messages:
                    content = getattr(message, "content", message.get("content") if isinstance(message, dict) else "")
                    st.session_state.messages.append({"role": "assistant", "content": {"type": "text", "content": content}})
                    render_assistant_message({"type": "text", "content": content})
                
                data_meta = value.get("data_meta", {})
                print(data_meta)
                if data_meta:
                    st.session_state.messages.append({"role": "assistant", "content": {"type": "data", "content": data_meta}})
                    render_assistant_message({"type": "data", "content": data_meta})
