"""
Premium Chat Page — Centered conversational AI layout with animated
empty state, streaming-style thinking indicator, and follow-up cards.
"""

import time
import sys
from pathlib import Path

import streamlit as st

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def render_chat_page():
    """Render the main premium chat interface."""
    from frontend.components.chat_message import render_chat_message
    from frontend.components.landing import render_landing_hero

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    msgs = st.session_state["messages"]

    # ── Empty state: show landing hero ────────────────────────────────────────
    if not msgs:
        render_landing_hero()
    else:
        # ── Chat header ────────────────────────────────────────────────────────
        st.markdown(
            "<div style='margin-bottom:1rem;'>"
            "<span style='font-size:0.75rem;color:#3D5070;'>⚖️ Citizen Rights Assistant  ·  "
            "Active Session</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        # Render all messages
        for idx, msg in enumerate(msgs):
            render_chat_message(msg, idx)

        # ── Follow-up questions ────────────────────────────────────────────────
        follow_ups = st.session_state.get("follow_up_questions", [])
        if follow_ups and msgs:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.markdown(
                "<div style='font-size:0.72rem;color:#3D5070;font-weight:600;"
                "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;'>"
                "Related Questions</div>",
                unsafe_allow_html=True,
            )
            fu_cols = st.columns(min(len(follow_ups), 3))
            for i, q in enumerate(follow_ups[:3]):
                with fu_cols[i]:
                    if st.button(q, key=f"fu_{i}", use_container_width=True):
                        st.session_state["prefill_query"] = q
                        st.rerun()

    # ── Chat input ─────────────────────────────────────────────────────────────
    prefill   = st.session_state.pop("prefill_query", None)
    user_input = st.chat_input(
        "Ask about your rights, government services, legal procedures…"
    )

    if prefill and not user_input:
        user_input = prefill

    if user_input:
        _process_query(user_input)
        st.rerun()


def _process_query(query: str):
    """Send query through local pipeline and render response."""
    response_mode = st.session_state.get("response_mode", "normal")

    # Show user bubble immediately
    user_msg = {"role": "user", "content": query}
    st.session_state["messages"].append(user_msg)
    with st.chat_message("user"):
        st.markdown(query)

    # Show assistant thinking state
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown(
            """
            <div class="ai-thinking">
                <div class="dot-pulse"></div>
                <div class="dot-pulse"></div>
                <div class="dot-pulse"></div>
                <span style="margin-left:6px;">Searching government documents…</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            result = _query_via_pipeline(query, response_mode)

            if result.get("error"):
                placeholder.error(f"Error: {result['error']}")
                return

            response_content = result.get("content") or result.get("response", "")
            placeholder.markdown(response_content)

            assistant_msg = {
                "role":             "assistant",
                "content":          response_content,
                "citations":        result.get("citations", []),
                "response_mode":    response_mode,
                "latency_seconds":  (
                    result.get("latency_seconds")
                    or result.get("latency", {}).get("total", 0)
                ),
                "faithfulness_score": result.get("faithfulness_score"),
                "relevancy_score":   result.get("relevancy_score"),
            }
            st.session_state["messages"].append(assistant_msg)
            st.session_state["follow_up_questions"] = result.get("follow_up_questions", [])

        except Exception as e:
            placeholder.error(f"Failed to generate response: {e}")


def _query_via_pipeline(query: str, response_mode: str) -> dict:
    """Query the local RAG pipeline."""
    if "pipeline" not in st.session_state:
        from src.orchestration.graph import RAGPipeline
        with st.spinner("Initializing system components…"):
            st.session_state["pipeline"] = RAGPipeline()

    pipeline   = st.session_state["pipeline"]
    start_time = time.time()
    result     = pipeline.query_with_state({"query": query, "response_mode": response_mode})
    latency    = round(time.time() - start_time, 2)

    return {
        "role":              "assistant",
        "content":           result.get("response", ""),
        "response":          result.get("response", ""),
        "citations":         result.get("citations", []),
        "latency_seconds":   latency,
        "latency":           result.get("latency", {}),
        "follow_up_questions": result.get("follow_up_questions", []),
        "source_chunks":     result.get("source_chunks", []),
        "faithfulness_score": result.get("faithfulness_score"),
        "relevancy_score":   result.get("relevancy_score"),
    }
