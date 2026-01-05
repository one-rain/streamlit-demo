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
    st.subheader("📊 自由维度数据探索器")

    meta = parsed.get("meta", {})
    chart_id = meta.get("id")
    default_x_field = "年份"
    default_metrics = meta.get("metrics", meta.get("series", []))
    default_group_options = meta.get("group", [])
    default_chart_type = "bar" if meta.get("type") not in ["pie", "bar"] else meta.get("type")

    # 生成年份选项
    year_options = sorted(df[default_x_field].unique().tolist()) if default_x_field in df.columns else []

    # Fallback 组维度选项
    if not default_group_options:
        all_cols = meta.get("columns", list(df.columns))
        metric_set = set(default_metrics)
        default_group_options = [c for c in all_cols if c != default_x_field and c not in metric_set]

    if not hasattr(st.session_state, "charts"):
        st.session_state["charts"] = {}
    if chart_id not in st.session_state["charts"]:
        st.session_state["charts"][chart_id] = {
            "x": year_options[0] if year_options else None,
            "metrics": default_metrics,
            "group": None,
            "type": default_chart_type
        }
    state = st.session_state["charts"][chart_id]

    with st.expander("图表配置", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            x_value = st.selectbox(
                "年份",
                options=year_options,
                index=(year_options.index(state.get("x")) if state.get("x") in year_options else 0) if year_options else 0,
                key=f"x_dim_{chart_id}"
            )
            chart_type = st.radio(
                "图表类型",
                options=["pie", "bar"],
                index=["pie", "bar"].index(state.get("type", default_chart_type)),
                key=f"chart_{chart_id}",
                horizontal=True
            )
        with col2:
            y_metrics = st.multiselect(
                "指标(Y轴)",
                options=default_metrics,
                default=state.get("metrics", default_metrics),
                key=f"metrics_{chart_id}"
            )
            group_col = st.selectbox(
                "分组维度（group）",
                options=["无"] + default_group_options,
                index=0,
                key=f"group_{chart_id}"
            )

    if not y_metrics:
        st.warning("请至少选择一个指标")
        return

    group_dim = None if group_col == "无" else group_col
    state.update({
        "x": x_value,
        "metrics": y_metrics,
        "group": group_dim,
        "type": chart_type
    })

    # 过滤到选定年份
    df_year = df[df[default_x_field] == x_value] if x_value is not None else df

    # 饼图（使用第一个指标）
    if chart_type == "pie":
        metric = y_metrics[0]
        slice_dim = group_dim if group_dim else (default_group_options[0] if default_group_options else None)
        if not slice_dim:
            st.warning("无可用分组维度用于饼图")
            return
        pie_df = df_year.groupby(slice_dim)[metric].sum().reset_index()
        fig = px.pie(
            pie_df,
            values=metric,
            names=slice_dim,
            title=f"{x_value}年 {metric} 按 {slice_dim} 分布"
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
        return

    # 柱状图（支持单/多指标）
    category_dim = group_dim if group_dim else (default_group_options[0] if default_group_options else None)
    if not category_dim:
        st.warning("无可用分组维度用于柱状图")
        return

    if len(y_metrics) == 1:
        metric = y_metrics[0]
        agg_df = df_year.groupby(category_dim)[metric].sum().reset_index()
        fig = px.bar(
            agg_df,
            x=category_dim,
            y=metric,
            color=category_dim,
            title=f"{x_value}年 各{category_dim}的 {metric}"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_title=category_dim, yaxis_title=metric)
        st.plotly_chart(fig, use_container_width=True)
    else:
        melted = df_year.melt(
            id_vars=[category_dim],
            value_vars=y_metrics,
            var_name="指标",
            value_name="值"
        )
        fig = px.bar(
            melted,
            x=category_dim,
            y="值",
            color="指标",
            barmode="group",
            title=f"{x_value}年 各{category_dim}的多指标对比"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_title=category_dim, yaxis_title="值")
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
