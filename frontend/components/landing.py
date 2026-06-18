"""
Premium Landing Hero — Full-screen hero with animated feature cards,
workflow section, statistics, and suggested queries.
"""

import streamlit as st

def render_landing_hero():
    """Render the premium full-featured landing page hero section."""

    # ── Hero Section ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;padding:3rem 1rem 2rem 1rem;
                    animation:fadeInUp 0.6s ease forwards;">
            <div style="display:inline-flex;align-items:center;gap:8px;
                        background:rgba(37,99,235,0.1);border:1px solid rgba(37,99,235,0.2);
                        border-radius:100px;padding:5px 16px;margin-bottom:1.5rem;">
                <div style="width:6px;height:6px;border-radius:50%;
                             background:#3B82F6;animation:dotPulse 1.4s infinite;"></div>
                <span style="font-size:0.75rem;color:#60A5FA;font-weight:600;
                              letter-spacing:0.06em;text-transform:uppercase;">
                    Production-Grade RAG System · Live
                </span>
            </div>
            <h1 style="
                font-size:clamp(2rem,5vw,3.5rem);
                font-weight:900;
                letter-spacing:-0.03em;
                line-height:1.1;
                margin-bottom:1.25rem;
                background:linear-gradient(135deg,#F0F4FF 0%,#93C5FD 50%,#818CF8 100%);
                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;
            ">
                Citizen Rights &amp;<br>Government Services
            </h1>
            <p style="
                color:#94A3C0;
                font-size:clamp(0.95rem,2vw,1.15rem);
                max-width:680px;
                margin:0 auto 2rem auto;
                line-height:1.7;
                font-weight:400;
            ">
                A production AI assistant that helps citizens understand legal rights,
                government schemes, consumer protection, labor laws, cybercrime procedures,
                and public services — powered by official government documents with
                trustworthy citations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
