import streamlit as st
import html

def render_user_message(content):
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; align-items: flex-start; margin-bottom: 1rem;">
        <div style="background-color: #f0f2f6; color: #31333f; padding: 1rem; border-radius: 0.5rem; margin-right: 0.5rem; max-width: 70%; text-align: left;">
            <div style="white-space: pre-wrap;">{html.escape(content)}</div>
        </div>
        <div style="font-size: 1.5rem; line-height: 1.5;">👤</div>
    </div>
    """, unsafe_allow_html=True)