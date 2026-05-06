import streamlit as st
from streamlit_javascript import st_javascript
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

if "count" not in st.session_state:
    st.session_state.count = 0
    logger.info("Streamlit 启动")

st.title("Streamlit LocalStorage Demo")
st.divider()

count = st.session_state.count

logger.info(f"-->当前写入次数：{count}")

def write_token_to_localstorage(token: str):
    js_code = f"localStorage.setItem('token', '{token}');"
    st_javascript(js_code)

def read_token_from_localstorage():
    token_value = st_javascript('''localStorage.getItem('token');''')
    logger.info(f"从 LocalStorage 读取到的 Token: {token_value}")
    return token_value

# 输入token
token_input = st.text_input("输入 token")

# 写入 localStorage
if st.button("写入 localStorage"):
    if token_input:
        logger.info(f"写入 token 到 localStorage: {token_input}")
        write_token_to_localstorage(token_input)
        count += 1
        logger.info(f"写入次数增加到：{count}")
        time.sleep(0.5) 
        st.rerun() # 强制整个脚本重新运行以捕获最新状态
    else:
        st.warning("请输入 token")

logger.info(f"上次写入次数：{count}, 当前次数：{st.session_state.count}")

token_value = read_token_from_localstorage()
if token_value and token_value != 0:
    st.success(f"读取成功: {token_value}")
else:
    st.info("正在尝试从浏览器同步 Token...")
