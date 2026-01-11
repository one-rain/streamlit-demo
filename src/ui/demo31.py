import json
import uuid
import streamlit as st
import pandas as pd
import plotly.express as px
from agent.medal_agent import build_graph
from utils.cache import CacheType, global_cache
from utils.common_util import render_user_message

st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀自由维度探索Demo1")


def plotly_chart(chart_id: str, data: list[dict]):
    df = pd.DataFrame(data, columns=data[0].keys())
    st.subheader("📊 自由维度数据探索器")

    default_x_field = "年份"
    default_metrics = ["金牌", "银牌", "铜牌"]
    default_group_options = ["国家"]
    default_chart_type = "bar"

    # 生成年份选项
    year_options = sorted(df[default_x_field].unique().tolist()) if default_x_field in df.columns else []

    # Fallback 组维度选项
    if not default_group_options:
        all_cols = ["", ""]
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

    # 柱状图（支持单/多指标）
    category_dim = group_dim if group_dim else (default_group_options[0] if default_group_options else None)
    if not category_dim:
        st.warning("无可用分组维度用于柱状图")
        return
    
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
    st.plotly_chart(fig, width="stretch", key=f"bar2_{chart_id}")


def render_assistant_message(content: list[str], data_meta: dict):
    for item in content:
        st.markdown(item)
    
    data = None
    if data_meta and data_meta.get("store_type") == "local":
        st.markdown("#### 本地图表")
        store_key = str(uuid.uuid4())
        data = data_meta.get("data", [])
    elif data_meta and data_meta.get("store_type") == "memory":
        st.markdown("#### 内存图表")
        store_key = data_meta.get("store_key", "")
        key = f"{CacheType.KEY_PAYLOAD_DATA}:{store_key}"
        data = global_cache.get(key, CacheType.HOT)
    
    if data:
        plotly_chart(store_key, data)


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": ["请输入问题，我会尽力回答。"], "data_meta": {}}]


for msg in st.session_state.messages:
    if msg["role"] == "user" or msg["role"] == "human":
        render_user_message(msg["content"])
    else:
        with st.chat_message("assistant"):
            render_assistant_message(msg["content"], msg["data_meta"])


if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user_message(prompt)

    with st.chat_message("assistant"):
        for state in build_graph().stream({"messages": prompt}, 
            config={"configurable": {"data_type": "medal_width", "store_type": "local"}}
        ):
            for key, value in state.items():
                #print(f"{key}: {value}")
                messages = value.get("messages", [])
                contents = []
                for message in messages:
                    raw_content = getattr(message, "content", message.get("content") if isinstance(message, dict) else "")
                    contents.append(raw_content)
                
                render_assistant_message(contents, value.get("data_meta", {}))
                st.session_state.messages.append({"role": "assistant", "content": contents, "data_meta": value.get("data_meta", {})})
