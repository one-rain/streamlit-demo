import streamlit as st
import numpy as np

with st.chat_message("assistant"):
    st.write("Hello human")
    st.write(st.context.locale)
    st.write(st.context.timezone)
    st.bar_chart(np.random.randn(30, 3))