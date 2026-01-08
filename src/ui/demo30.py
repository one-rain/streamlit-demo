import json
import uuid
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from agent import simple1_agent
from utils.common_util import render_user_message


st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀基于返回类型的类型展示简易Demo")


def chart_bar_simple(data: list):
    # 简易柱状图
    df = pd.DataFrame(data, columns=data[0].keys())
    x_col = "国家"
    y_col = "奖牌数"
    df = df.set_index(x_col)
    metrics=["金牌", "银牌", "铜牌"]
    st.bar_chart(metrics, stack=False)

def chart_bar_altair(data: list):
    df = pd.DataFrame(data, columns=data[0].keys())
    x_col = "国家"
    y_col = "奖牌数"
    metrics=["金牌", "银牌", "铜牌"]
    if metrics and len(metrics) > 1:
        melted = df.melt(id_vars=[x_col], value_vars=metrics, var_name="🏅奖牌", value_name="奖牌数")
        chart = alt.Chart(melted).mark_bar().encode(
            x=alt.X(f"{x_col}:N"),
            y=alt.Y("奖牌数:Q"),
            color="🏅奖牌:N",
            tooltip=[x_col, "🏅奖牌", "奖牌数"]
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        print("no metrics")
        if y_col not in df.columns and metrics:
            df[y_col] = df[metrics].sum(axis=1)
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(f"{x_col}:N"),
            y=alt.Y(f"{y_col}:Q"),
            tooltip=[x_col, y_col]
        )
        st.altair_chart(chart, use_container_width=True)

def chart_bar_plotly(id: str, data: list):
    idx = f"table_{id}"
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
    st.plotly_chart(fig, key=idx)
    with st.expander("查看当前数据详情"):
        st.dataframe(df, key=idx)


def render_assistant_message(content):
    if content.startswith("["):
        id = str(uuid.uuid4())
        obj_data = json.loads(content)
        print(obj_data)
        # 求 id 的模数
        mod = hash(id) % 4
        if mod == 0:
            chart_bar_simple(obj_data)
        elif mod == 1:
            chart_bar_altair(obj_data)
        elif mod == 2:
            chart_bar_plotly(id, obj_data)
        elif mod == 3:
            st.json(obj_data)
        else:
            st.dataframe(obj_data)
    else:
        st.markdown(content)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    if msg["role"] == "user":
        render_user_message(msg["content"])
    else:
        with st.chat_message(msg["role"]):
            render_assistant_message(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user_message(prompt)

    with st.chat_message("assistant"):
        for state in simple1_agent.graph1.stream({"messages": st.session_state.messages}):
            for key, value in state.items():
                #print(f"{key}: {value}")
                messages = value.get("messages", [])
                for message in messages:
                    raw_content = getattr(message, "content", message.get("content") if isinstance(message, dict) else "")
                    st.session_state.messages.append({"role": "assistant", "content": raw_content})
                    render_assistant_message(raw_content)