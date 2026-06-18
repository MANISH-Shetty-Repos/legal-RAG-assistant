"""
Global premium CSS styles for Citizen Rights & Government Services Assistant.
Loaded once in app.py via inject_global_css().
"""


GLOBAL_CSS = """
<style>
/* ── Google Fonts ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── CSS Variables ────────────────────────────────────────────────────── */
:root {
  --bg-base:       #0A0E1A;
  --bg-surface:    #0F1629;
  --bg-elevated:   #151D35;
  --bg-card:       #1A2340;
  --bg-hover:      #1E2A47;

  --border-subtle: #1E2D4A;
  --border-mid:    #263354;
  --border-strong: #2E3D64;

  --text-primary:  #F0F4FF;
  --text-secondary:#94A3C0;
  --text-muted:    #5C6E8A;
  --text-caption:  #3D5070;

  --blue-primary:  #2563EB;
  --blue-accent:   #3B82F6;
  --blue-light:    #60A5FA;
  --blue-glow:     rgba(37, 99, 235, 0.25);

  --indigo:        #6366F1;
  --purple:        #8B5CF6;
  --green:         #10B981;
  --amber:         #F59E0B;
  --red:           #EF4444;
  --orange:        #F97316;

  --radius-sm:     6px;
  --radius-md:     10px;
  --radius-lg:     16px;
  --radius-xl:     24px;
  --radius-full:   9999px;

  --shadow-sm:  0 1px 3px rgba(0,0,0,0.4);
  --shadow-md:  0 4px 16px rgba(0,0,0,0.5);
  --shadow-lg:  0 10px 40px rgba(0,0,0,0.6);
  --shadow-glow:0 0 24px rgba(37,99,235,0.2);

  --transition: 0.2s cubic-bezier(0.4,0,0.2,1);
}

/* ── Base Reset ───────────────────────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* ── App Background ───────────────────────────────────────────────────── */
.stApp {
  background: var(--bg-base) !important;
  color: var(--text-primary) !important;
}

/* ── Hide Streamlit Chrome ────────────────────────────────────────────── */
#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { background-color: rgba(0, 0, 0, 0) !important; }

.stDeployButton { display: none; }

/* ── Scrollbar ────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-mid); border-radius: var(--radius-full); }
::-webkit-scrollbar-thumb:hover { background: var(--border-strong); }

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--bg-surface) !important;
  border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding-top: 0 !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────── */
.stButton > button {
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  font-size: 0.875rem !important;
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border-mid) !important;
  background: var(--bg-elevated) !important;
  color: var(--text-secondary) !important;
  transition: all var(--transition) !important;
  letter-spacing: -0.01em !important;
}
.stButton > button:hover {
  border-color: var(--border-strong) !important;
  background: var(--bg-hover) !important;
  color: var(--text-primary) !important;
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--blue-primary) 0%, #1D4ED8 100%) !important;
  border: none !important;
  color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, var(--blue-accent) 0%, var(--blue-primary) 100%) !important;
  box-shadow: 0 4px 16px var(--blue-glow) !important;
}

/* ── Inputs ───────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border-mid) !important;
  color: var(--text-primary) !important;
  border-radius: var(--radius-md) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--blue-primary) !important;
  box-shadow: 0 0 0 2px var(--blue-glow) !important;
  outline: none !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label {
  color: var(--text-secondary) !important;
  font-size: 0.8rem !important;
  font-weight: 500 !important;
}

/* ── Selectbox ────────────────────────────────────────────────────────── */
.stSelectbox > div > div {
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border-mid) !important;
  color: var(--text-primary) !important;
  border-radius: var(--radius-md) !important;
}

/* ── Chat Input ───────────────────────────────────────────────────────── */
[data-testid="stChatInput"] {
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border-mid) !important;
  border-radius: var(--radius-lg) !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: var(--text-primary) !important;
  font-family: 'Inter', sans-serif !important;
}

/* ── Chat Messages ────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  padding: 0.5rem 0 !important;
}

/* ── Expander ─────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-subtle) !important;
  border-radius: var(--radius-md) !important;
}
[data-testid="stExpander"] summary {
  color: var(--text-secondary) !important;
  font-size: 0.85rem !important;
}

/* ── Divider ──────────────────────────────────────────────────────────── */
hr { border-color: var(--border-subtle) !important; margin: 0.75rem 0 !important; }

/* ── Metric ───────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-subtle) !important;
  border-radius: var(--radius-md) !important;
  padding: 1rem !important;
}
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 0.75rem !important; }
[data-testid="stMetricValue"] { color: var(--text-primary) !important; }

/* ── Info / Warning / Error ───────────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--radius-md) !important;
  font-size: 0.875rem !important;
}

/* ── File Uploader ────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
  background: var(--bg-elevated) !important;
  border: 2px dashed var(--border-mid) !important;
  border-radius: var(--radius-lg) !important;
}

/* ── Spinner ──────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] { color: var(--blue-accent) !important; }

/* ── Tables ───────────────────────────────────────────────────────────── */
.stDataFrame { border-radius: var(--radius-md) !important; }
.stTable { border-radius: var(--radius-md) !important; }

/* ── Custom Static Sidebar Radio (nav) ────────────────────────────────── */
.stRadio > div {
  gap: 2px !important;
}
.stRadio label {
  border-radius: var(--radius-sm) !important;
  padding: 6px 10px !important;
  color: var(--text-secondary) !important;
  font-size: 0.875rem !important;
  cursor: pointer;
  transition: all var(--transition);
}
.stRadio label:hover {
  background: var(--bg-elevated) !important;
  color: var(--text-primary) !important;
}

/* ── Custom Component Classes ────────────────────────────────────────── */
.premium-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  transition: all var(--transition);
}
.premium-card:hover {
  border-color: var(--border-mid);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 1.25rem 1rem;
  text-align: center;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.badge-blue   { background: rgba(59,130,246,0.12); color: #60A5FA; border: 1px solid rgba(59,130,246,0.2); }
.badge-green  { background: rgba(16,185,129,0.12); color: #34D399; border: 1px solid rgba(16,185,129,0.2); }
.badge-amber  { background: rgba(245,158,11,0.12);  color: #FCD34D; border: 1px solid rgba(245,158,11,0.2); }
.badge-red    { background: rgba(239,68,68,0.12);   color: #F87171; border: 1px solid rgba(239,68,68,0.2); }
.badge-purple { background: rgba(139,92,246,0.12);  color: #A78BFA; border: 1px solid rgba(139,92,246,0.2); }

.section-title {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-caption);
  padding: 0.5rem 0;
}

.ai-thinking {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
  font-size: 0.85rem;
  font-style: italic;
  padding: 4px 0;
}
.dot-pulse {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--blue-accent);
  animation: dotPulse 1.4s infinite ease-in-out;
}
.dot-pulse:nth-child(2) { animation-delay: 0.2s; }
.dot-pulse:nth-child(3) { animation-delay: 0.4s; }
@keyframes dotPulse {
  0%, 60%, 100% { opacity: 0.2; transform: scale(0.8); }
  30%            { opacity: 1;   transform: scale(1.2); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeInUp 0.4s ease forwards; }

/* Citation chips */
.cite-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(59,130,246,0.08);
  border: 1px solid rgba(59,130,246,0.18);
  border-radius: var(--radius-full);
  padding: 4px 12px;
  font-size: 0.78rem;
  color: var(--blue-light);
  cursor: pointer;
  transition: all var(--transition);
  margin: 2px;
}
.cite-chip:hover {
  background: rgba(59,130,246,0.18);
  border-color: rgba(59,130,246,0.4);
  transform: translateY(-1px);
}

/* Skeleton loading */
.skeleton {
  background: linear-gradient(90deg, var(--bg-card) 25%, var(--bg-elevated) 50%, var(--bg-card) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Auth card */
.auth-glass {
  background: rgba(15, 22, 41, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-mid);
  border-radius: var(--radius-xl);
  padding: 2.5rem;
  box-shadow: var(--shadow-lg), var(--shadow-glow);
  max-width: 420px;
  margin: 0 auto;
}

/* Toast-like success banner */
.toast-success {
  background: rgba(16,185,129,0.1);
  border: 1px solid rgba(16,185,129,0.25);
  border-radius: var(--radius-md);
  padding: 10px 16px;
  color: #34D399;
  font-size: 0.875rem;
  font-weight: 500;
}
</style>
"""


def inject_global_css():
    """Inject the global premium CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
