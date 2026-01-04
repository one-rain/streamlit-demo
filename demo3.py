import html
import json
import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
from agent import agent2

st.set_page_config(layout="wide")
st.title("🦜🔗 Quickstart App")
st.caption("🚀基于返回类型的类型展示简易Demo")

def render_user_message(content):
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; align-items: flex-start; margin-bottom: 1rem;">
        <div style="background-color: #f0f2f6; color: #31333f; padding: 1rem; border-radius: 0.5rem; margin-right: 0.5rem; max-width: 70%; text-align: left;">
            <div style="white-space: pre-wrap;">{html.escape(content)}</div>
        </div>
        <div style="font-size: 1.5rem; line-height: 1.5;">👤</div>
    </div>
    """, unsafe_allow_html=True)


def parse_display_message(raw_content: str):
    try:
        obj = json.loads(raw_content)
        if isinstance(obj, dict) and "type" in obj:
            return obj
    except Exception:
        pass
    return None


def render_message(content):
    parsed = parse_display_message(content)

    if not parsed:
        st.markdown(content)
        return

    t = parsed["type"]
    if t == "markdown":
        st.markdown(parsed["payload"]["data"])
    elif t == "json":
        st.json(parsed["payload"]["data"])
    elif t == "table":
        st.dataframe(parsed["payload"]["data"])
    elif t == "chart":
        # 简易柱状图
        print(parsed)
        df = pd.DataFrame(parsed["payload"]["data"], columns=parsed["payload"]["columns"])
        df = df.set_index(parsed["payload"]["x"])
        st.bar_chart(df[parsed["payload"]["series"]], stack=False)

        #st.plotly_chart(parsed["data"])
    else:
        print(f"Unknown type: {t}")
        st.text(content)

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

    for state in agent2.graph.stream({"messages": st.session_state.messages}):
        for key, value in state.items():
            #print(f"{key}: {value}")
            messages = value.get("messages", [])
            msg_count = len(messages)
            if msg_count > 0:
                st.session_state.messages.append({"role": "assistant", "content": messages[-1].content})
            for msg in messages:
                raw_content = getattr(msg, "content", msg.get("content") if isinstance(msg, dict) else "")
                render_message(raw_content)
