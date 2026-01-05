import html
import json
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from agent import simple_agent

st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀自由维度数据探索展示简易Demo")

# 该方式会在页面左侧生成选项配置，如果有对话中有多个图表，将会导致选项配置冲突。所以，该方式不适合在对话中使用。

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


def chart_bar_plotly(parsed: dict):
    df = pd.DataFrame(parsed["data"], columns=parsed["meta"]["columns"])
    st.subheader(f"📊 自由维度数据探索器")

    meta = parsed.get("meta", {})
    print(meta)
    default_x = meta.get("x", "国家")
    default_metrics = meta.get("series", ["奖牌总数"])
    default_chart_type = meta.get("type", "bar")
    chart_id = meta.get("id")

    if not hasattr(st.session_state, "charts"):
        st.session_state["charts"] = {}
    
    if chart_id not in st.session_state["charts"]:
        st.session_state["charts"][chart_id] = {
            "x": default_x,
            "metrics": default_metrics,
            "columns": [],
            "type": default_chart_type
        }

    state = st.session_state["charts"][chart_id]
    print(state)
    
    with st.expander("图表配置", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            x_dim = st.selectbox(
                "X轴维度",
                options=meta.get("columns", list(df.columns)),
                index=(meta.get("columns", list(df.columns)).index(default_x) if default_x in meta.get("columns", list(df.columns)) else 0),
                key=f"x_dim_{chart_id}"
            )

            chart_type = st.radio(
                "图表类型",
                ["bar", "line"],
                index=["bar", "line"].index(state.get("type", default_chart_type)),
                key=f"chart_{chart_id}",
                horizontal=True
            )
        
        with col2:
            y_metrics = st.multiselect(
                "Y轴指标",
                options=[c for c in df.columns if c != x_dim],
                default=state.get("metrics", default_metrics),
                key=f"metrics_{chart_id}"
            )

            group_col = st.selectbox(
                "分组维度（columns）",
                options=["无"] + [c for c in meta.get("columns", list(df.columns)) if c != x_dim],
                index=0,
                key=f"columns_{chart_id}"
            )

    if not y_metrics:
        st.warning("请至少选择一个指标")
        return

    group_dim = None if group_col == "无" else group_col

    # ---------- 更新 state ----------
    state.update({
        "x": x_dim,
        "metrics": y_metrics,
        "columns": [group_dim] if group_dim else [],
        "type": chart_type
    })

    # ---------- 数据聚合 ----------
    group_fields = [x_dim] + ([group_dim] if group_dim else [])
    agg_df = df.groupby(group_fields)[y_metrics].sum().reset_index()

    # ---------- 构造图表 ----------
    if len(y_metrics) == 1:
        y = y_metrics[0]

        chart = (
            alt.Chart(agg_df)
            .mark_bar() if chart_type == "bar"
            else alt.Chart(agg_df).mark_line(point=True)
        ).encode(
            x=alt.X(f"{x_dim}:O", title=x_dim),
            y=alt.Y(f"{y}:Q", title=y),
            color=group_dim if group_dim else alt.value("#4C78A8"),
            tooltip=list(agg_df.columns)
        )

    else:
        melted = agg_df.melt(
            id_vars=group_fields,
            value_vars=y_metrics,
            var_name="指标",
            value_name="值"
        )

        chart = (
            alt.Chart(melted)
            .mark_bar() if chart_type == "bar"
            else alt.Chart(melted).mark_line(point=True)
        ).encode(
            x=alt.X(f"{x_dim}:O", title=x_dim),
            y=alt.Y("值:Q"),
            color="指标:N",
            column=group_dim if group_dim else alt.value(None),
            tooltip=list(melted.columns)
        )

    st.altair_chart(chart, use_container_width=True)


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
