"""
Premium sidebar — Brand, new chat, response mode, documents panel, quick topics.
"""

import streamlit as st
from pathlib import Path

project_root = Path(__file__).parent.parent.parent

CATEGORY_CONFIG = [
    ("Fundamental Rights",    "What are my fundamental rights?"),
    ("RTI Act",               "How do I file an RTI application?"),
    ("Consumer Protection",   "Consumer Protection Act rights"),
    ("Labor Laws",            "Labor rights for workers in India"),
    ("Property Rights",       "Property rights and documentation"),
    ("Government Schemes",    "Welfare schemes eligibility"),
    ("Cybercrime",            "How to report cybercrime online?"),
    ("Traffic Rules",         "Traffic violation fines and rules"),
]


def render_sidebar():
    """Render the premium sidebar."""

    _render_brand()
    st.markdown("<hr style='border-color:#1E2D4A;margin:0.5rem 0;'>", unsafe_allow_html=True)

    # ── New Chat ──────────────────────────────────────────────────────────
    if st.button("New Chat", key="sb_new_chat",
                 use_container_width=True, type="primary"):
        st.session_state["messages"] = []
        st.session_state["active_conversation_id"] = None
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Page Navigation ────────────────────────────────────────────────────
    _render_section_title("Navigation")
    nav_page = st.selectbox(
        "menu_select",
        ["Chat Interface", "Evaluation Dashboard"],
        index=0 if st.session_state.get("page", "Chat") == "Chat" else 1,
        label_visibility="collapsed",
    )
    if nav_page == "Chat Interface" and st.session_state.get("page") != "Chat":
        st.session_state["page"] = "Chat"
        st.rerun()
    elif nav_page == "Evaluation Dashboard" and st.session_state.get("page") != "Evaluation":
        st.session_state["page"] = "Evaluation"
        st.rerun()

    st.markdown("<hr style='border-color:#1E2D4A;margin:0.5rem 0;'>", unsafe_allow_html=True)

    # ── Response Mode ──────────────────────────────────────────────────────
    _render_section_title("Response Mode")
    mode = st.selectbox(
        "mode_select",
        ["normal", "simple", "legal"],
        index=["normal", "simple", "legal"].index(
            st.session_state.get("response_mode", "normal")),
        label_visibility="collapsed",
        format_func=lambda m: {
            "normal": "Normal",
            "simple": "Simple",
            "legal":  "Legal",
        }[m],
    )
    st.session_state["response_mode"] = mode
    st.markdown("<hr style='border-color:#1E2D4A;margin:0.5rem 0;'>", unsafe_allow_html=True)

    # ── Documents Panel ────────────────────────────────────────────────────
    _render_documents_panel()
    st.markdown("<hr style='border-color:#1E2D4A;margin:0.5rem 0;'>", unsafe_allow_html=True)

    # ── Quick Topics ───────────────────────────────────────────────────────
    _render_section_title("Quick Topics")
    for label, query in CATEGORY_CONFIG:
        if st.button(label, key=f"cat_{label}", use_container_width=True):
            st.session_state["prefill_query"] = query
            st.rerun()

    st.markdown("<hr style='border-color:#1E2D4A;margin:0.5rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;color:#3D5070;font-size:0.65rem;"
        "padding:8px 0 4px 0;'>v2.1.0 — Citizen Assistant</div>",
        unsafe_allow_html=True,
    )


# ── Private helpers ───────────────────────────────────────────────────────────

def _render_brand():
    st.markdown(
        """
        <div style="padding:1.25rem 0.5rem 0.75rem 0.5rem;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="
                    width:32px;height:32px;border-radius:9px;flex-shrink:0;
                    background:linear-gradient(135deg,#2563EB,#6366F1);
                    display:flex;align-items:center;justify-content:center;
                    font-size:1rem;box-shadow:0 4px 12px rgba(37,99,235,0.35);">⚖️</div>
                <div>
                    <div style="font-size:0.82rem;font-weight:700;color:#F0F4FF;
                                letter-spacing:-0.01em;">Citizen Rights</div>
                    <div style="font-size:0.65rem;color:#3D5070;
                                text-transform:uppercase;letter-spacing:0.07em;">AI Assistant</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_section_title(title: str):
    st.markdown(
        "<div style='font-size:0.67rem;font-weight:700;letter-spacing:0.1em;"
        "text-transform:uppercase;color:#3D5070;padding:4px 0 6px 0;'>"
        + title + "</div>",
        unsafe_allow_html=True,
    )


def _get_pipeline():
    """Get or create the RAG pipeline singleton."""
    if "pipeline" not in st.session_state:
        from src.orchestration.graph import RAGPipeline
        with st.spinner("Initializing system…"):
            st.session_state["pipeline"] = RAGPipeline()
    return st.session_state["pipeline"]


def _render_documents_panel():
    """Documents panel with auto-ingest upload and document list."""
    _render_section_title("Documents")

    with st.expander("Documents", expanded=False):
        # ── Upload + Auto-Ingest ──────────────────────────────────────────
        st.markdown(
            "<div style='font-size:0.75rem;font-weight:600;color:#94A3C0;"
            "margin-bottom:6px;'>Add Documents</div>",
            unsafe_allow_html=True,
        )
        uploaded_files = st.file_uploader(
            "Upload files",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
            key="sb_doc_uploader",
            label_visibility="collapsed",
        )

        # Auto-ingest on upload (no button needed)
        if uploaded_files:
            pipeline = _get_pipeline()
            user_id = 0
            raw_dir = project_root / "data" / "raw"
            raw_dir.mkdir(parents=True, exist_ok=True)

            for uf in uploaded_files:
                save_path = raw_dir / uf.name
                with open(save_path, "wb") as fh:
                    fh.write(uf.getbuffer())
                with st.spinner(f"Ingesting {uf.name}..."):
                    try:
                        res = pipeline.ingest_file(str(save_path), uploaded_by_id=user_id)
                        st.toast(f"Ingested {res['filename']} — {res['chunks']} chunks")
                    except Exception as e:
                        st.error(f"Failed: {uf.name} — {e}")
            st.rerun()

        st.markdown("<hr style='border-color:#1E2D4A;margin:0.5rem 0;'>", unsafe_allow_html=True)

        # ── Document List ─────────────────────────────────────────────────
        pipeline = _get_pipeline()
        try:
            all_chunks = pipeline.vector_store.get_all_chunks()
        except Exception:
            all_chunks = []

        if not all_chunks:
            st.markdown(
                "<div style='font-size:0.75rem;color:#5C6E8A;text-align:center;"
                "padding:10px 0;'>No documents indexed.</div>",
                unsafe_allow_html=True,
            )
            return

        # Group by filename
        files_dict = {}
        for chunk in all_chunks:
            meta = chunk.get("metadata", {})
            fname = meta.get("filename", "Unknown")
            ftype = meta.get("file_type", "unknown").upper()
            if fname not in files_dict:
                files_dict[fname] = {"type": ftype, "chunks": 0}
            files_dict[fname]["chunks"] += 1

        st.markdown(
            "<div style='font-size:0.75rem;font-weight:600;color:#94A3C0;"
            "margin-bottom:6px;'>All Documents</div>",
            unsafe_allow_html=True,
        )

        for fname, info in files_dict.items():
            st.markdown(
                "<div style='font-size:0.75rem;color:#F0F4FF;padding:4px 0;"
                "white-space:nowrap;overflow:hidden;text-overflow:ellipsis;' title='"
                + fname + "'>"
                + fname
                + " <span style='font-size:0.65rem;color:#5C6E8A;'>("
                + info["type"] + ", " + str(info["chunks"]) + " chk)</span></div>",
                unsafe_allow_html=True,
            )
            if st.button("Delete", key=f"sb_del_{fname}", use_container_width=True):
                pipeline.vector_store.delete_by_filename(fname)
                pipeline._rebuild_bm25_index()
                st.toast(f"Deleted {fname}")
                st.rerun()
