import uuid
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from agent.medal_agent import build_medal_graph
from utils.cache import CacheType, global_cache
from utils.common_util import render_user_message

st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀数据与消息分离的简易Demo")


def chart_bar_plotly1(id: str, data: list[dict]):
    df = pd.DataFrame(data, columns=data[0].keys())
    #year_options = df["年份"].unique().tolist()
    
    custom_colors = {
        "中国": "#FF0000",  # 红色
        "美国": "#002868",  # 蓝色
        "英国": "#FFA500"   # 橙色
    }

    fig1 = px.bar(
        df, 
        x="年份", 
        y="数量", 
        color="国家", 
        barmode="group",
        color_discrete_map=custom_colors,
        category_orders={"国家": ["中国", "美国", "英国"]},  # 确保顺序正确
        text="奖牌" # 
        )

    st.plotly_chart(fig1, key=f"chart_bar_plotly1:{id}")

    year_options = df["年份"].unique().tolist()
    default_year = st.session_state.get("default_year", year_options[-1])

    with st.expander("图表配置", expanded=True):
        x_value = st.selectbox(
            "年份",
            options=year_options,
            index=year_options.index(default_year),
            key=f"x_dim_{id}"
        )
        st.session_state["default_year"] = x_value
        title = f"奥运奖牌{x_value}年度榜单"

    df_year = df[df["年份"] == x_value]
    fig2 = px.bar(
        df_year, 
        x="国家", 
        y="数量", 
        color="奖牌", 
        barmode="group",
        color_discrete_map={
            "金牌": "#FFD700",  # 金牌颜色
            "银牌": "#C0C0C0",  # 银牌颜色
            "铜牌": "#CD7F32"   # 铜牌颜色
        },
        category_orders={"奖牌": ["金牌", "银牌", "铜牌"]},  # 确保顺序正确
        title=title,
        text_auto=True
        )
    st.plotly_chart(fig2, key=f"chart_bar_plotly2:{id}")
 
    medal_gold = df[df["奖牌"] == "金牌"]
    medal_silver = df[df["奖牌"] == "银牌"]
    medal_bronze = df[df["奖牌"] == "铜牌"]

    #medal_gold[medal_gold['国家'] == '中国']['数量'].tolist(),

    data = [
        go.Bar(
            x=['2016', '2020', '2024'],
            y=[34, 32, 28],
            name='中国 - 金牌',
            offsetgroup="金牌"
        ),
        go.Bar(
            x=['2016', '2020', '2024'],
            y=[31, 49, 37],
            name='美国 - 金牌',
            offsetgroup="金牌"
        ),
        go.Bar(
            x=['2016', '2020', '2024'],
            y=[27, 23, 48],
            name='英国 - 金牌',
            offsetgroup="金牌"
        ),
        go.Bar(
            x=['2016', '2020', '2024'],
            y=[28, 24, 33],
            name='中国 - 银牌',
            offsetgroup="银牌"
        ),
        go.Bar(
            x=['2016', '2020', '2024'],
            y=[28, 24, 33],
            name='美国 - 银牌',
            offsetgroup="银牌"
        ),
        go.Bar(
            x=['2016', '2020', '2024'],
            y=[28, 24, 33],
            name='英国 - 银牌',
            offsetgroup="银牌"
        ),
        go.Bar(
            x=['2016', '2020', '2024'],
            y=[28, 24, 33],    
            name='中国 - 铜牌',
            offsetgroup="铜牌"
        ),
        go.Bar(
            x=['2016', '2020', '2024'],
            y=[28, 24, 33],    
            name='美国 - 铜牌',
            offsetgroup="铜牌"
        ),
        go.Bar(
            x=['2016', '2020', '2024'],
            y=[28, 24, 33],    
            name='英国 - 铜牌',
            offsetgroup="铜牌"
        ),
    ]

    layout = go.Layout(
        title={
            'text': '奥运奖牌历届榜单'
        },
        xaxis={
            'title': {
                'text': '年份'
            }
        },
        yaxis={
            'title': {
                'text': '奖牌数量'
            }
        },
        barmode='stack'
    )
    
    fig3 = go.Figure(data=data, layout=layout)
    st.plotly_chart(fig3, key=f"chart_bar_plotly3:{id}")


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
        chart_bar_plotly1(store_key, data)


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": ["请输入问题，我会尽力回答。"], "data_meta": {}}]


for msg in st.session_state.messages:
    if msg["role"] == "user" or msg["role"] == "human":
        render_user_message(msg["content"])
    else:
        with st.chat_message("assistant"):
            render_assistant_message(msg["content"], msg["data_meta"])


config = {"configurable": {"data_type": "medal_long"}}

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user_message(prompt)

    with st.chat_message("assistant"):
        for state in build_medal_graph().stream({"messages": prompt}, config=config):
            for key, value in state.items():
                #print(f"{key}: {value}")
                messages = value.get("messages", [])
                data_meta = value.get("data_meta", {})
                contents = []
                for message in messages:
                    raw_content = getattr(message, "content", message.get("content") if isinstance(message, dict) else "")
                    contents.append(raw_content)
                render_assistant_message(contents, data_meta)
                st.session_state.messages.append({"role": "assistant", "content": contents, "data_meta": data_meta})
