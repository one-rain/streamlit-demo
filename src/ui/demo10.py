import streamlit as st
from vega_datasets import data


with st.chat_message("assistant"):
    st.write("Hello human")
    st.write(f"当前语言：{st.context.locale}")
    st.write(f"当前时区：{st.context.timezone}")
    
    st.markdown("### 数据集：")
    st.json(data.list_datasets())
    
    st.markdown("### Barley信息：")
    barley = data.barley()
    st.dataframe(barley.describe())

    filtered_df = barley[barley["year"] == 1931]

    st.markdown("### 1931年Barley数据表格：")
    st.write(filtered_df)

    st.markdown("### 1931年Barley数据可视化：")
    st.bar_chart(filtered_df, x="variety", y="yield", color="site")
