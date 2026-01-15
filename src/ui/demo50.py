import uuid
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from agent.chart_agent import build_chart_graph
from agent.schema import ChartType
from utils.common_util import render_user_message

st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀前端根据后端提供的ChartSpec渲染图表")

# 前端根据后端提供的ChartSpec渲染图表

def render_chart_line(id: str, chart_spec: dict):
    print("start render line chart...")
    field_schemas = chart_spec["dataset"]["field_schemas"]
    chart_mapping = chart_spec["mapping"]
    columns_dict = {}
    columns = []
    data_id = chart_spec["dataset"]["id"]
    x_format = None
    for schema in field_schemas:
        columns_dict[schema["name"]] = schema["title"]
        columns.append(schema["name"])
        if schema.get("type", "") in ["date", "datetime"] and schema.get("format"):
            x_format = schema["format"]
        

    df = pd.DataFrame(chart_spec["dataset"]["data"], columns=columns)
    df.rename(columns=columns_dict, inplace=True)

    options_size = len(chart_mapping.get("dim_options", []))
    chart_config_key = f"chart_config_{id}"
    if chart_config_key not in st.session_state:
        st.session_state[chart_config_key] = {"data_id": data_id}
    
    chart_config = st.session_state[chart_config_key]

    metric_option = chart_mapping.get("metric_option", {}) or {}
    y_value = chart_spec["mapping"]["y_axis"]
    df_options = None
    if options_size > 0 or metric_option.get("values"):
        with st.expander("筛选条件", expanded=True):
            df_options = df.copy()
            col1, col2, col3 = st.columns(3) # 筛选条件分列，可以有多行
            for i, dim in enumerate(chart_mapping.get("dim_options", [])):
                key = f"{data_id}_x_{i}"
                default_x_index = dim["values"].index(chart_config.get(key)) if chart_config.get(key) else 0

                if i % 3 == 0:
                    col = col1
                elif i % 3 == 1:
                    col = col2
                else:
                    col = col3
                
                x_value = col.selectbox(
                    dim["label"],
                    options=dim["values"],
                    index=default_x_index,
                    key=f"{key}"
                )
                chart_config[key] = x_value
                st.session_state[chart_config_key] = chart_config
                df_options = df_options[df_options[dim["label"]] == x_value]
                
            key = f"{data_id}_y"
            default_y_index = metric_option["values"].index(chart_config.get(key)) if chart_config.get(key) else 0

            if metric_option.get("values"):
                final_size = options_size + 1
                if final_size % 3 == 0:
                    col = col1
                elif final_size % 3 == 1:
                    col = col2
                else:
                    col = col3
                
                y_value = col.selectbox(
                    metric_option.get("label", ""),
                    options=metric_option["values"],
                    index=default_y_index,
                    key=f"{key}"
                )
                chart_config[key] = y_value
                st.session_state[chart_config_key] = chart_config

    title = f"应用活跃趋势"

    x = chart_spec["mapping"]["x_axis"]
    color = chart_mapping["series"][0]
    data_for_plot = df_options if df_options is not None else df
    fig = px.line(data_for_plot, x=x, y=y_value, color=color, title=title, markers=True)
    # 格式化x轴日期显示
    if x_format:
        fig.update_xaxes(tickformat=x_format)
    
    st.plotly_chart(fig, width="stretch", key=f"line_{id}")
    with st.expander("数据明细", expanded=False):
        st.dataframe(
            df, 
            column_config={
                "日期": st.column_config.DateColumn("日期", format="YYYY-MM-DD"),
                "DAU": st.column_config.NumberColumn("DAU", format="accounting"),
            },
            hide_index=True
        )

def render_chart_bar(id: str, chart_spec: dict):
    print("start render bar chart...")
    field_schemas = chart_spec["dataset"]["field_schemas"]
    chart_mapping = chart_spec["mapping"]
    columns_dict = {}
    columns = []
    data_id = chart_spec["dataset"]["id"]
    for schema in field_schemas:
        columns_dict[schema["name"]] = schema["title"]
        columns.append(schema["name"])

    df = pd.DataFrame(chart_spec["dataset"]["data"], columns=columns)
    df.rename(columns=columns_dict, inplace=True)

    title = f"应用活跃趋势柱状图1"
    fig = px.bar(
        df[df["日期"] == "2024-01-01"], 
        x="公司", 
        y="DAU",
        color="应用",
        barmode="group",
        title=title, 
        text_auto=True
    )

    st.plotly_chart(fig, key=f"bar_{id}")
    
def render_chart_pie(id: str, chart_spec: dict):
    print("start render pie chart...")
    
    field_schemas = chart_spec["dataset"]["field_schemas"]
    chart_mapping = chart_spec["mapping"]
    columns_dict = {}
    columns = []
    data_id = chart_spec["dataset"]["id"]
    x_format = None
    for schema in field_schemas:
        columns_dict[schema["name"]] = schema["title"]
        columns.append(schema["name"])

    df = pd.DataFrame(chart_spec["dataset"]["data"], columns=columns)
    df.rename(columns=columns_dict, inplace=True)

    title = f"应用活跃占比图"
    fig = px.pie(
        df[df["公司"] == "DaGeDa"][df["日期"] == "2024-01-01"], 
        values="DAU",
        names="应用",
        title=title,
        hover_data=['DAU'], 
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig, key=f"pie_{id}")
    

def render_table(id: str, chart_spec: dict):
    print("start render table...")
    field_schemas = chart_spec["dataset"]["field_schemas"]
    columns_dict = {}
    columns = []
    for schema in field_schemas:
        columns_dict[schema["name"]] = schema["title"]
        columns.append(schema["name"])

    df = pd.DataFrame(chart_spec["dataset"]["data"], columns=columns)
    df.rename(columns=columns_dict, inplace=True)
    st.dataframe(df, hide_index=True, key=f"table_{id}")


def render_assistant_message(chart_id: str, content: list[str], chart_spec: dict):
    for item in content:
        st.markdown(item)
    
    if chart_spec and "dataset" in chart_spec:
        
        chart_type = chart_spec.get("chart_type", "")
        if chart_type == ChartType.LINE.value:
            render_chart_line(chart_id, chart_spec)
        elif chart_type == ChartType.BAR.value:
            render_chart_bar(chart_id, chart_spec)
        elif chart_type == ChartType.PIE.value:
            render_chart_pie(chart_id, chart_spec)
        else:
            render_table(chart_id, chart_spec)


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": ["请输入问题，我会尽力回答。"], "chart_spec": {}, "id": str(uuid.uuid4())}]


for msg in st.session_state.messages:
    if msg["role"] == "user" or msg["role"] == "human":
        render_user_message(msg["content"])
    else:
        with st.chat_message("assistant"):
            render_assistant_message(msg["id"], msg["content"], msg["chart_spec"])


config = {"configurable": {"data_type": "medal_long"}}

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user_message(prompt)
    id = str(uuid.uuid4())

    with st.chat_message("assistant"):
        for state in build_chart_graph().stream({"messages": prompt}, config=config):
            for key, value in state.items():
                #print(f"{key}: {value}")
                messages = value.get("messages", [])
                chart_spec = value.get("chart_spec", {})
                contents = []
                for message in messages:
                    raw_content = getattr(message, "content", message.get("content") if isinstance(message, dict) else "")
                    contents.append(raw_content)
                render_assistant_message(id, contents, chart_spec)
                st.session_state.messages.append({"role": "assistant", "content": contents, "chart_spec": chart_spec, "id": id})
