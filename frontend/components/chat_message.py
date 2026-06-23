"""
Premium chat message component — Elegant AI message cards with
citations, feedback, metadata badges, and animated thinking state.
"""

import streamlit as st


def render_chat_message(msg: dict, index: int = 0):
    """Render a single premium chat message bubble."""
    role    = msg.get("role", "user")
    content = msg.get("content", "")

    with st.chat_message(role):
        # User messages
        if role == "user":
            st.markdown(content)
            return

        # ── Assistant message wrapper ──────────────────────────────────────────
        st.markdown(content)

        latency   = msg.get("latency_seconds")
        citations = msg.get("citations") or []
        mode      = msg.get("response_mode", "normal")
        
        # ── Metadata badges ────────────────────────────────────────────────────
        badges_html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 6px 0;'>"
        if latency is not None:
            badges_html += (
                f"<span class='badge badge-blue'>{latency:.2f}s</span>"
            )
        if citations:
            badges_html += (
                f"<span class='badge badge-green'>{len(citations)} source{'s' if len(citations)!=1 else ''}</span>"
            )
        mode_colors = {"normal": "badge-blue", "simple": "badge-amber", "legal": "badge-purple"}
        if mode:
            m_color = mode_colors.get(mode, "badge-blue")
            m_label = mode.capitalize()
            badges_html += (
                f"<span class='badge {m_color}'>"
                f"{m_label} Mode</span>"
            )
        badges_html += "</div>"
        st.markdown(badges_html, unsafe_allow_html=True)

        # ── Citation chips ─────────────────────────────────────────────────────
        if citations:
            _render_citation_chips(citations, index)


def _render_citation_chips(citations: list, index: int):
    """Render citation source chips with expandable details."""
    with st.expander(f"Verified Sources  ({len(citations)})", expanded=False):
        for i, cite in enumerate(citations):
            filename   = cite.get("filename", cite.get("source", "Unknown"))
            page       = cite.get("page_number", cite.get("page", "N/A"))
            section    = cite.get("section", "")
            confidence = cite.get("score", cite.get("confidence", None))

            # Build confidence badge
            conf_badge_html = ""
            if confidence is not None:
                try:
                    conf_float = float(confidence)
                    pct = int(conf_float * 100) if conf_float <= 1 else int(conf_float)
                    color = "#34D399" if pct >= 80 else "#FCD34D" if pct >= 60 else "#F87171"
                    conf_badge_html = (
                        "<span style='background:rgba(16,185,129,0.1);"
                        "border:1px solid rgba(16,185,129,0.2);"
                        "border-radius:100px;padding:2px 8px;"
                        "font-size:0.7rem;color:" + color + ";'>"
                        + str(pct) + "%</span>"
                    )
                except (ValueError, TypeError):
                    pass

            # Build optional section line
            section_html = ""
            if section:
                section_html = (
                    "<div style='font-size:0.75rem;color:#5C6E8A;margin-top:2px;'>"
                    + str(section) + "</div>"
                )

            # Assemble full card HTML without nested f-strings
            card_html = (
                "<div style='background:#1A2340;border-left:3px solid #2563EB;"
                "border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:8px;'>"
                "<div style='display:flex;justify-content:space-between;"
                "align-items:flex-start;gap:8px;'>"
                "<div style='flex:1;overflow:hidden;'>"
                "<div style='font-size:0.85rem;font-weight:600;color:#93C5FD;"
                "white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>"
                + str(filename) +
                "</div>"
                + section_html +
                "</div>"
                "<div style='display:flex;gap:6px;align-items:center;flex-shrink:0;'>"
                + conf_badge_html +
                "<span style='background:#263354;border:1px solid #2E3D64;"
                "border-radius:6px;padding:2px 8px;"
                "font-size:0.75rem;color:#94A3C0;'>pg. "
                + str(page) +
                "</span>"
                "</div>"
                "</div>"
                "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)



