import html
import json
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from agent import simple_agent

st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀基于返回类型的类型展示简易Demo")

def render_user_message(content):
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; align-items: flex-start; margin-bottom: 1rem;">
        <div style="background-color: #f0f2f6; color: #31333f; padding: 1rem; border-radius: 0.5rem; margin-right: 0.5rem; max-width: 70%; text-align: left;">
            <div style="white-space: pre-wrap;">{html.escape(content)}</div>
        </div>
        <div style="font-size: 1.5rem; line-height: 1.5;">👤</div>
    </div>
    """, unsafe_allow_html=True)


def parse_display_message(raw_content):
    try:
        obj = json.loads(raw_content)
        if isinstance(obj, dict) and "type" in obj:
            return obj
    except Exception:
        pass
    return None

def chart_bar_simple(parsed: dict):
    # 简易柱状图
    df = pd.DataFrame(parsed["data"], columns=parsed["meta"]["columns"])
    df = df.set_index(parsed["meta"]["x"])
    st.bar_chart(df[parsed["meta"]["series"]], stack=False)

def chart_bar_altair(parsed: dict):
    df = pd.DataFrame(parsed["data"], columns=parsed["meta"]["columns"])
    x_col = parsed["meta"]["x"]
    y_col = parsed["meta"]["y"]
    series = parsed.get("meta", {}).get("series", [])
    if series and len(series) > 1:
        melted = df.melt(id_vars=[x_col], value_vars=series, var_name="🏅奖牌", value_name="奖牌数")
        chart = alt.Chart(melted).mark_bar().encode(
            x=alt.X(f"{x_col}:N"),
            y=alt.Y("奖牌数:Q"),
            color="🏅奖牌:N",
            tooltip=[x_col, "🏅奖牌", "奖牌数"]
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        print("no series")
        if y_col not in df.columns and series:
            df[y_col] = df[series].sum(axis=1)
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(f"{x_col}:N"),
            y=alt.Y(f"{y_col}:Q"),
            tooltip=[x_col, y_col]
        )
        st.altair_chart(chart, use_container_width=True)

def chart_bar_plotly(parsed: dict):
    df = pd.DataFrame(parsed["data"], columns=parsed["meta"]["columns"])
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
    idx = f"plotly_{parsed['meta']['type']}_{parsed['meta']['id']}"
    st.plotly_chart(fig, key=idx)
    with st.expander("查看当前数据详情"):
        idx = f"table_{parsed['meta']['id']}"
        st.dataframe(df, key=idx)


def render_message(content):
    parsed = parse_display_message(content)

    if not parsed:
        if isinstance(content, (dict, list)):
            st.json(content)
        else:
            st.markdown(content)
        return

    t = parsed["type"]
    if t == "markdown":
        st.markdown(parsed["data"])
    elif t == "json":
        st.json(parsed["data"])
    elif t == "table":
        st.dataframe(parsed["data"])
    elif t == "chart":
        # chart_bar_simple(parsed)
        # chart_bar_altair(parsed)
        chart_bar_plotly(parsed)
    else:
        print(f"Unknown type: {t}")
        st.text(content)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    if msg["role"] == "user":
        render_user_message(msg["content"])
    else:
        with st.chat_message(msg["role"]):
            render_message(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user_message(prompt)

    for state in simple_agent.graph.stream({"messages": st.session_state.messages}):
        for key, value in state.items():
            #print(f"{key}: {value}")
            messages = value.get("messages", [])
            msg_count = len(messages)
            if msg_count > 0:
                st.session_state.messages.append({"role": "assistant", "content": messages[-1].content})
            for msg in messages:
                raw_content = getattr(msg, "content", msg.get("content") if isinstance(msg, dict) else "")
                render_message(raw_content)
