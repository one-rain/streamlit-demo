import streamlit as st
from streamlit.components.v1 import html

st.title("Streamlit LocalStorage Demo")
st.divider()

# 输入token
token_input = st.text_input("输入 token")

# 写入 localStorage
if st.button("写入 localStorage"):
    if token_input:
        # 使用 HTML 组件执行 localStorage 操作
        html(f"""
        <script>
            localStorage.setItem('token', '{token_input}');
            console.log('Token written to localStorage:', '{token_input}');
        </script>
        """)
        st.success("token 已写入 localStorage")
    else:
        st.warning("请输入 token")

st.divider()
