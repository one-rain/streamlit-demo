import streamlit as st
from agent import openai_agent
from utils.common_util import render_user_message

st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀基于LangChain Graph的简易Demo")


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
                final_msg = content
                placeholder.write(content)
    st.session_state.messages.append({"role": "assistant", "content": final_msg})
