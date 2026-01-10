import json
import uuid
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from agent import barley_agent
from utils.common_util import render_user_message


st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀基于返回类型的类型展示简易Demo")


def chart_bar_simple(data: list):
    # 简易柱状图
    df = pd.DataFrame(data, columns=data[0].keys())
    st.bar_chart(df, x="variety", y="yield", color="site", width="stretch", stack=False)

def chart_bar_altair(id: str, data: list):
    df = pd.DataFrame(data, columns=data[0].keys())
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(x="variety", y="yield", color="site", tooltip=["variety", "yield", "site"])
    )
    st.altair_chart(chart, width="stretch", key=f"bar0_{id}")

def chart_bar_plotly1(id: str, data: list):
    idx = f"bar1_{id}"
    df = pd.DataFrame(data, columns=data[0].keys())  
    df.index = df.index + 1 # 将索引值全部加1
    #此种方式适用于长数据格式
    # 长数据格式：每个指标是一行记录
    # 宽数据格式：每个指标是一列记录
    fig = px.bar(
        df, 
        x='variety', 
        y='yield', # 如果是宽数据格式，此处应该是指标数组
        color='site', 
        title="小麦产量分布柱状图1", 
        text_auto=True
    )

    st.plotly_chart(fig, key=idx)
    with st.expander("查看当前数据详情"):
        # 指定列顺序
        target_cols = ['year', 'variety', 'site', 'yield']
        cols = [c for c in target_cols if c in df.columns]
        # 补充剩余列
        cols += [c for c in df.columns if c not in cols]
        # 隐藏索引并显示
        st.table(df[cols])


def chart_bar_plotly2(id: str, data: list):
    # 实现按照品种总产量排行榜（按site固定顺序）

    idx = f"bar2_{id}"
    columns = list(data[0].keys())
    df = pd.DataFrame(data, columns=columns)

    # 步骤1：按variety和site聚合产量（sum）
    df_grouped = df.groupby(['variety', 'site'], as_index=False)['yield'].sum()

    # 步骤2：计算每个variety的总产量，用于排序
    df_variety_total = df_grouped.groupby('variety')['yield'].sum().reset_index()
    df_variety_total.columns = ['variety', 'total_yield']

    # 步骤3：合并总产量到聚合数据，并按总产量降序排序
    df_merged = pd.merge(df_grouped, df_variety_total, on='variety')
    # 按总产量降序、site固定顺序排序（这里site顺序用数据集原生唯一值顺序）
    fixed_site_order = df['site'].unique().tolist()  # 固定site顺序
    df_merged['site'] = pd.Categorical(df_merged['site'], categories=fixed_site_order, ordered=True)
    df_merged = df_merged.sort_values(['total_yield', 'site'], ascending=[False, True])

    fig = px.bar(
        df_merged, 
        x='yield', 
        y='variety', 
        color='site', 
        orientation='h',    # 水平柱状图
        title="小麦产量分布柱状图2", 
        labels={'yield': '产量', 'variety': '品种', 'site': '种植地点'},
        hover_data={'total_yield': False},  # 隐藏总产量的hover显示
        text_auto=True
    )

    # 重点：强制x轴到顶部
    fig.update_layout(
        # 将x轴移到顶部
        xaxis=dict(
            side='top',
            title='产量',
            linecolor='black',       # x轴线颜色
            linewidth=1,              # x轴线宽度
            title_font=dict(size=12),
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title='品种',
            title_font=dict(size=12),
            tickfont=dict(size=10),
            categoryorder='total ascending'  # 按总产量升序排列y轴（Plotly从下往上画，所以升序=最大的在上面）
        ),
        # 调整图例位置（固定site顺序）
        legend=dict(
            title='种植地点',
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5,
            traceorder='normal'  # 按fixed_site_order显示图例
        ),
        # 调整图表大小和边距
        width=900,
        height=600,
        margin=dict(l=100, r=20, t=50, b=80)
    )

    # 4. 优化柱状图样式
    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color='white'
    )

    # 5. 添加总产量标签到右侧
    # 只需要唯一的variety和对应的total_yield
    df_unique_total = df_merged[['variety', 'total_yield']].drop_duplicates()
    
    # 增加一个Scatter trace用于显示文本
    fig.add_trace(go.Scatter(
        x=df_unique_total['total_yield'],
        y=df_unique_total['variety'],
        text=df_unique_total['total_yield'].apply(lambda x: f"  <b>{x:.1f}</b>"), # 格式化保留1位小数并加粗
        mode='text',
        textposition='middle right',
        showlegend=False,
        hoverinfo='skip'
    ))

    # 适当扩展x轴范围，防止文字被遮挡
    max_yield = df_unique_total['total_yield'].max()
    fig.update_layout(xaxis_range=[0, max_yield * 1.15])

    st.plotly_chart(fig, key=idx)


def render_assistant_message(content):
    if content.startswith("["):
        id = str(uuid.uuid4())
        obj_data = json.loads(content)
        # 求 id 的模数
        mod = hash(id) % 4
        if mod == 0:
            st.markdown("#### 简易柱状图")
            chart_bar_simple(obj_data)
        elif mod == 1:
            st.markdown("#### Altair 柱状图")
            chart_bar_altair(id, obj_data)
        elif mod == 2:
            st.markdown("#### Plotly 柱状图1")
            chart_bar_plotly1(id, obj_data)
        elif mod == 3:
            st.markdown("#### Plotly 柱状图2")
            chart_bar_plotly2(id, obj_data)
        else:
            st.markdown("#### 数据表")
            st.dataframe(obj_data)
    else:
        st.markdown(content)


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": ["How can I help you?"]}]


for msg in st.session_state.messages:
    if msg["role"] == "user" or msg["role"] == "human":
        render_user_message(msg["content"])
    else:
        with st.chat_message("assistant"):
            for content in msg["content"]:
                render_assistant_message(content)


if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user_message(prompt)

    with st.chat_message("assistant"):
        for state in barley_agent.graph1.stream({"messages": st.session_state.messages}):
            for key, value in state.items():
                #print(f"{key}: {value}")
                messages = value.get("messages", [])
                contents = []
                for message in messages:
                    raw_content = getattr(message, "content", message.get("content") if isinstance(message, dict) else "")
                    contents.append(raw_content)
                    render_assistant_message(raw_content)
                st.session_state.messages.append({"role": "assistant", "content": contents})
