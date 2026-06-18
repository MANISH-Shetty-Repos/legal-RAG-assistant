"""
Premium Evaluation Dashboard Page — Displays run-time query metrics,
interactive RAGAS/judge report analysis, and manual evaluation controls.
"""

# pyrefly: ignore [missing-import]
import streamlit as st
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent


def render_evaluation_page():
    """Render the main premium evaluation page."""
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <h1 style="margin: 0; font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #60A5FA, #A78BFA); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Evaluation & Analytics Dashboard
            </h1>
            <p style="margin: 0.25rem 0 0 0; color: #94A3C0; font-size: 0.95rem;">
                Monitor latency, answer quality, and run automated RAG evaluation cycles.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tabs for Session Metrics vs Automated Suite
    tab1, tab2 = st.tabs(["Active Session Metrics", "Automated Evaluation Suite"])

    with tab1:
        _render_session_metrics()

    with tab2:
        _render_automated_suite()


def _render_session_metrics():
    """Render metrics for the current session's queries."""
    st.subheader("Current Chat Session Analytics")

    msgs = st.session_state.get("messages", [])
    assistant_msgs = [m for m in msgs if m.get("role") == "assistant"]

    if not assistant_msgs:
        st.info("No assistant responses in this session yet. Start chatting to see analytics!")
        return

    # Calculate session statistics
    latencies = [m.get("latency_seconds", 0) for m in assistant_msgs if m.get("latency_seconds") is not None]
    faithfulness_scores = [
        m.get("faithfulness_score") for m in assistant_msgs if m.get("faithfulness_score") is not None
    ]
    relevancy_scores = [
        m.get("relevancy_score") for m in assistant_msgs if m.get("relevancy_score") is not None
    ]

    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0
    avg_relevancy = sum(relevancy_scores) / len(relevancy_scores) if relevancy_scores else 0

    # Layout metric cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{avg_latency:.2f}s</div>
                <div class="metric-label">Average Latency</div>
                <div style="font-size:0.7rem; color:#5C6E8A; margin-top:4px;">Target: < 3.00s</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        status_color = "#34D399" if avg_faithfulness >= 0.85 else "#FCD34D" if avg_faithfulness >= 0.7 else "#F87171"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {status_color};">{avg_faithfulness * 100:.1f}%</div>
                <div class="metric-label">Avg. Faithfulness (No Hallucination)</div>
                <div style="font-size:0.7rem; color:#5C6E8A; margin-top:4px;">Target: > 85.0%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        status_color = "#34D399" if avg_relevancy >= 0.8 else "#FCD34D" if avg_relevancy >= 0.6 else "#F87171"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {status_color};">{avg_relevancy * 100:.1f}%</div>
                <div class="metric-label">Avg. Answer Relevancy</div>
                <div style="font-size:0.7rem; color:#5C6E8A; margin-top:4px;">Target: > 80.0%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Detailed session query breakdown
    st.markdown("<h4 style='color:#F0F4FF; margin-top:1.5rem;'>Session Query History & Scores</h4>", unsafe_allow_html=True)

    for idx, msg in enumerate(assistant_msgs):
        query = msgs[msgs.index(msg) - 1].get("content", "Unknown Query") if msgs.index(msg) > 0 else "Unknown"
        lat = msg.get("latency_seconds", 0)
        faith = msg.get("faithfulness_score")
        rel = msg.get("relevancy_score")
        citations = msg.get("citations") or []

        faith_str = f"{int(faith*100)}%" if faith is not None else "N/A"
        rel_str = f"{int(rel*100)}%" if rel is not None else "N/A"

        st.markdown(
            f"""
            <div style="background:#131B31; border: 1px solid #1E2D4A; border-radius:8px; padding:12px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:600; color:#93C5FD; font-size:0.85rem;">Q{idx+1}: {query[:80]}...</span>
                    <span style="font-size:0.75rem; color:#5C6E8A;">{lat:.2f}s</span>
                </div>
                <div style="margin-top:6px; display:flex; gap:12px; font-size:0.75rem;">
                    <span>🛡️ Faithfulness: <strong style="color:{'#34D399' if faith == 1.0 else '#F87171'}">{faith_str}</strong></span>
                    <span>🎯 Relevancy: <strong style="color:{'#34D399' if rel == 1.0 else '#F87171'}">{rel_str}</strong></span>
                    <span>📚 Citations: <strong>{len(citations)}</strong></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_automated_suite():
    """Render interface for triggering and viewing RAGAS evaluation suite reports."""
    st.subheader("Automated Evaluation Suite")

    # 1. Run Evaluation Trigger
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Run Automated Test Suite", use_container_width=True, type="primary"):
            _run_eval_script()

    with col2:
        st.markdown(
            "<span style='color:#5C6E8A; font-size:0.8rem; vertical-align:middle; line-height:2.5rem;'>"
            "Runs all test cases from evaluation/testset.csv and saves a detailed report."
            "</span>",
            unsafe_allow_html=True,
        )

    # 2. Select and visualize saved reports
    reports_dir = project_root / "evaluation" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_files = sorted(list(reports_dir.glob("eval_report_*.json")), reverse=True)

    if not report_files:
        st.info("No evaluation reports found. Run the test suite to generate a report.")
        return

    st.markdown("<hr style='border-color:#1E2D4A; margin:1.5rem 0;'>", unsafe_allow_html=True)
    st.subheader("Past Evaluation Reports")

    report_options = {rf.name: rf for rf in report_files}
    selected_report_name = st.selectbox(
        "Select Report to View",
        list(report_options.keys()),
        format_func=lambda n: _format_report_filename(n),
    )

    if selected_report_name:
        rf = report_options[selected_report_name]
        try:
            with open(rf, "r", encoding="utf-8") as fh:
                report_data = json.load(fh)
            _render_report_details(report_data)
        except Exception as e:
            st.error(f"Error loading report {selected_report_name}: {e}")


def _format_report_filename(name: str) -> str:
    """Format file name containing epoch into readable date."""
    try:
        epoch = int(name.split("_")[-1].split(".")[0])
        dt = datetime.fromtimestamp(epoch)
        return dt.strftime("%Y-%m-%d %I:%M:%S %p") + f" ({name})"
    except Exception:
        return name


def _run_eval_script():
    """Execute the evaluation script via subprocess and show progress."""
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.info("Starting evaluation run... (running test queries against local Qwen/Llama)")
    progress_bar.progress(10)

    try:
        # Run scripts/run_evaluation.py using the virtual env python
        venv_python = str(project_root / "venv" / "bin" / "python")
        if not Path(venv_python).exists():
            venv_python = "python3"

        cmd = [venv_python, str(project_root / "scripts" / "run_evaluation.py")]

        progress_bar.progress(30)
        status_text.info("Querying local model and compiling metrics... This can take 1-2 minutes...")

        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )

        progress_bar.progress(90)

        if res.returncode == 0:
            status_text.success("Evaluation complete! Report saved.")
            progress_bar.progress(100)
            time.sleep(1)
            st.rerun()
        else:
            status_text.error(f"Evaluation failed (code {res.returncode}): {res.stderr or res.stdout}")
    except Exception as e:
        status_text.error(f"Failed to start evaluation process: {e}")


def _render_report_details(data: dict):
    """Render details of a selected evaluation report."""
    summary = data.get("summary", {})
    results = data.get("results", [])

    st.markdown(
        f"""
        <div style="background:rgba(30,41,59,0.5); padding:1rem; border-radius:10px; margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:space-between;">
                <span><strong>Total Test Cases:</strong> {summary.get('total_questions', 0)}</span>
                <span><strong>Report Generation:</strong> {data.get('timestamp', 'N/A')}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 metrics columns
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        avg_lat = summary.get("average_latency_seconds", 0)
        status_icon = "✅" if avg_lat < 3.0 else "⚠️"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{avg_lat:.2f}s</div>
                <div class="metric-label">{status_icon} Latency</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        faith = summary.get("average_faithfulness", 0)
        status_icon = "✅" if faith >= 0.85 else "❌"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'#34D399' if faith >= 0.85 else '#F87171'}">{faith*100:.1f}%</div>
                <div class="metric-label">{status_icon} Faithfulness</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        rel = summary.get("average_relevancy", 0)
        status_icon = "✅" if rel >= 0.80 else "❌"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'#34D399' if rel >= 0.80 else '#F87171'}">{rel*100:.1f}%</div>
                <div class="metric-label">{status_icon} Relevancy</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        corr = summary.get("average_correctness", 0)
        status_icon = "✅" if corr >= 0.80 else "❌"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'#34D399' if corr >= 0.80 else '#F87171'}">{corr*100:.1f}%</div>
                <div class="metric-label">{status_icon} Correctness</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c5:
        cit = summary.get("average_citation_recall", 0)
        status_icon = "✅" if cit >= 0.80 else "❌"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'#34D399' if cit >= 0.80 else '#F87171'}">{cit*100:.1f}%</div>
                <div class="metric-label">{status_icon} Citation Recall</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    c6, c7 = st.columns(2)
    with c6:
        cp = summary.get("average_context_precision", 0)
        status_icon = "✅" if cp >= 0.80 else "❌"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'#34D399' if cp >= 0.80 else '#F87171'}">{cp*100:.1f}%</div>
                <div class="metric-label">{status_icon} Context Precision</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c7:
        cr = summary.get("average_context_recall", 0)
        status_icon = "✅" if cr >= 0.80 else "❌"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'#34D399' if cr >= 0.80 else '#F87171'}">{cr*100:.1f}%</div>
                <div class="metric-label">{status_icon} Context Recall</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    hall = summary.get("average_hallucination_rate", 0)
    hall_icon = "✅" if hall <= 0.20 else "❌"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {'#34D399' if hall <= 0.20 else '#F87171'}">{hall*100:.1f}%</div>
            <div class="metric-label">{hall_icon} Hallucination Rate</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Detailed table of queries
    st.markdown("<h4 style='color:#F0F4FF; margin-top:2rem;'>Test Case Drill-Down</h4>", unsafe_allow_html=True)

    for r in results:
        rid = r.get("id", 0)
        q = r.get("question", "")
        exp = r.get("expected_answer", "")
        resp = r.get("response", "")
        metrics = r.get("metrics", {})
        ret_gt = r.get("retrieved_gt", False)
        cited_gt = r.get("cited_gt", False)

        with st.expander(f"Case {rid}: {q[:60]}..."):
            st.markdown(f"**Question:** {q}")
            st.markdown(f"**Expected Ground Truth Answer:**\n> {exp}")
            st.markdown(f"**Generated Response:**\n> {resp}")

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Core Metrics:**")
                st.markdown(f"- 🛡️ Faithfulness: `{metrics.get('faithfulness')}`")
                st.markdown(f"- 🎯 Relevancy: `{metrics.get('relevancy')}`")
                st.markdown(f"- ⚖️ Correctness: `{metrics.get('correctness')}`")
                st.markdown(f"- 📌 Context Precision: `{metrics.get('context_precision')}`")
                st.markdown(f"- 📌 Context Recall: `{metrics.get('context_recall')}`")
                st.markdown(f"- 🧠 Hallucination Rate: `{metrics.get('hallucination_rate')}`")
                st.markdown(f"- ⏱️ Latency: `{metrics.get('latency_seconds')}s`")
            with col_b:
                st.markdown("**Retrieval & Citation:**")
                st.markdown(f"- Ground Truth Source: `{r.get('gt_source')} (pg. {r.get('gt_page')})`")
                st.markdown(f"- Retrieved Ground Truth Source? {'Yes ✅' if ret_gt else 'No ❌'}")
                st.markdown(f"- Cited Ground Truth Source? {'Yes ✅' if cited_gt else 'No ❌'}")
