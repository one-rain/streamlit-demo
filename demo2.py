import re
import html
import streamlit as st
from agent import agent1

st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀基于LangChain Graph的简易Demo")

def render_user_message(content):
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; align-items: flex-start; margin-bottom: 1rem;">
        <div style="background-color: #f0f2f6; color: #31333f; padding: 1rem; border-radius: 0.5rem; margin-right: 0.5rem; max-width: 70%; text-align: left;">
            <div style="white-space: pre-wrap;">{html.escape(content)}</div>
        </div>
        <div style="font-size: 1.5rem; line-height: 1.5;">👤</div>
    </div>
    """, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    if msg["role"] == "user":
        render_user_message(msg["content"])
    else:
        st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user_message(prompt)

    assistant_box = st.chat_message("assistant")
    placeholder = assistant_box.empty()
    final_msg = ""
    for state in agent1.graph.stream({"messages": st.session_state.messages}):
        print("="*20)
        print(f"\nstate: {state}\n")
        for key, value in state.items():
            print(f"{key}: {value}")
            messages = value.get("messages", [])
            if messages:
                last = messages[-1]
                content = getattr(last, "content", last.get("content") if isinstance(last, dict) else "")
                #cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
                final_msg = content
                placeholder.write(content)
    st.session_state.messages.append({"role": "assistant", "content": final_msg})
