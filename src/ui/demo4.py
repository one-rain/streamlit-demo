import html
import json
import streamlit as st
import pandas as pd
import altair as alt
import plotly.figure_factory as ff
import plotly.express as px
from agent import simple_agent

st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀基于Tool Call 的简易Demo")

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
    df = pd.DataFrame(parsed["data"], columns=parsed["columns"])
    df = df.set_index(parsed["x"])
    st.bar_chart(df[parsed["series"]], stack=False)

def chart_bar_altair(parsed: dict):
    df = pd.DataFrame(parsed["data"], columns=parsed["columns"])
    x_col = parsed["x"]
    y_col = parsed["y"]
    series = parsed.get("series", [])
    if series and len(series) > 1:
        melted = df.melt(id_vars=[x_col], value_vars=series, var_name="类型", value_name="数值")
        chart = alt.Chart(melted).mark_bar().encode(
            x=alt.X(f"{x_col}:N"),
            y=alt.Y("数值:Q"),
            color="类型:N",
            tooltip=[x_col, "类型", "数值"]
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
    df = pd.DataFrame(parsed["data"], columns=parsed["columns"])
    x_col = parsed["x"]
    y_col = parsed["y"]
    series = parsed.get("series", [])
    title = parsed.get("meta", {}).get("title", "")

    if series and len(series) > 1:
        # Plotly Express 自动处理宽表格式，y传列表即可
        fig = px.bar(df, x=x_col, y=series, title=title, barmode="group")
    else:
        print("no series")
        if y_col not in df.columns and series:
            df[y_col] = df[series].sum(axis=1)
        
        fig = px.bar(df, x=x_col, y=y_col, title=title)

    st.plotly_chart(fig, use_container_width=True)

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
        st.markdown(parsed["payload"]["data"])
    elif t == "json":
        st.json(parsed["payload"]["data"])
    elif t == "table":
        st.dataframe(parsed["payload"]["data"])
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
