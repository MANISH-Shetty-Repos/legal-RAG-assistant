"""
Citizen Rights & Government Services Assistant
Main Streamlit entrypoint — Premium enterprise AI interface.
"""

import streamlit as st
import sys
from pathlib import Path
import logging

# Silence Streamlit's local sources watcher traceback/warning log pollution
logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Citizen Rights & Government Services Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Global Premium CSS ─────────────────────────────────────────────────
from frontend.styles import inject_global_css  # noqa: E402
inject_global_css()

# ── Session State Defaults ────────────────────────────────────────────────────
_DEFAULTS = {
    "messages":               [],
    "active_conversation_id": None,
    "response_mode":          "normal",
    "follow_up_questions":    [],
    "page":                   "Chat",
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v



# ── Sidebar + Page Router ─────────────────────────────────────────────────────
from frontend.components.sidebar import render_sidebar   # noqa: E402
from frontend.pages.chat import render_chat_page          # noqa: E402
from frontend.pages.evaluation import render_evaluation_page  # noqa: E402

with st.sidebar:
    render_sidebar()

if st.session_state.get("page", "Chat") == "Chat":
    render_chat_page()
else:
    render_evaluation_page()


