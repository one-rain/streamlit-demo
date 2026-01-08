import json
import uuid
import streamlit as st
import pandas as pd
import plotly.express as px
from agent import simple2_agent
from utils.common_util import render_user_message

st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀自由维度数据探索展示简易Demo")


def plotly_chart(chart_id: str, data: list[dict]):
    columns=["年份", "国家", "金牌", "银牌", "铜牌", "奖牌总数"]
    df = pd.DataFrame(data, columns=columns)
    st.subheader("📊 自由维度数据探索器")

    default_x_field = "年份"
    default_metrics = ["金牌", "银牌", "铜牌", "奖牌总数"]
    default_group_options = ["国家"]
    default_chart_type = "bar"

    # 生成年份选项
    year_options = sorted(df[default_x_field].unique().tolist()) if default_x_field in df.columns else []

    # Fallback 组维度选项
    if not default_group_options:
        all_cols = columns
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
        st.plotly_chart(fig, use_container_width=True, key=f"pie_{chart_id}")
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
        st.plotly_chart(fig, use_container_width=True, key=f"bar1_{chart_id}")
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
        st.plotly_chart(fig, use_container_width=True, key=f"bar2_{chart_id}")


def render_assistant_message(content):
    if content.startswith("{"):
        obj_data = json.loads(content)
        id = obj_data.get("id", "")
        plotly_chart(id, obj_data.get("data", []))
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
        for state in simple2_agent.graph1.stream({"messages": st.session_state.messages}):
            for key, value in state.items():
                #print(f"{key}: {value}")
                messages = value.get("messages", [])
                for message in messages:
                    raw_content = getattr(message, "content", message.get("content") if isinstance(message, dict) else "")
                    st.session_state.messages.append({"role": "assistant", "content": raw_content})
                    render_assistant_message(raw_content)
