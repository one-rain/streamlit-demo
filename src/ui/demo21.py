import streamlit as st
from agent import openai_agent
from utils.common_util import render_user_message


st.set_page_config(layout="wide", page_title="Demo - ChatBI", page_icon="🦜")
st.title("💬 ChatBI", text_alignment="center")
st.caption("🚀 基于LangChain Graph的简易Demo", text_alignment="center")

# ======================
# Session State 初始化
# ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ======================
# 会话状态：是否已 chatted（首轮展示热门问题）
# ======================
if "has_chatted" not in st.session_state:
    st.session_state.has_chatted = False

# ======================
# 历史消息渲染
# ======================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        render_user_message(msg["content"])
    else:
        st.chat_message(msg["role"]).write(msg["content"])

# ======================
# 🔥 热门问题（仅首轮展示）
# ======================
if not st.session_state.has_chatted:
    hot_questions = [
        "昨天的活跃用户是多少？",
        "本周销售额同比增长情况",
        "最近7天的新增用户",
        "异常波动最大的指标是什么？"
    ]
    with st.chat_message("assistant"):
        st.markdown("你可以试试下面这些问题 👇")

        for i, q in enumerate(hot_questions):
            if st.button(q, key=f"hot_q_{i}"): # 点击热门问题后，将问题存储到会话状态，用于后续处理
                st.session_state.pending_question = q
                st.rerun()

# ======================
# Chat 输入（统一入口）
# ======================
prompt = st.chat_input("请输入你的问题")

# 热门问题点击优先
if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question") # 从会话状态中弹出热门问题，确保仅处理一次

if prompt:
    st.session_state.has_chatted = True

    # 用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user_message(prompt)

    for state in openai_agent.graph.stream({"messages": st.session_state.messages}):
        print("="*20)
        print(f"\nstate: {state}\n")
        for key, value in state.items():
            print(f"{key}: {value}")
            messages = value.get("messages", [])
            if messages:
                last = messages[-1]
                content = getattr(last, "content", last.get("content") if isinstance(last, dict) else "")
                #cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
                st.chat_message("assistant").markdown(content)
                st.session_state.messages.append({"role": "assistant", "content": content})
        
