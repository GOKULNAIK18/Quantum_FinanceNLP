import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Quantum Finance", page_icon="⚛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: #050a14; color: #e2e8f0; }

    /* Hide default streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 3rem; max-width: 1400px; }

    /* Hero header */
    .hero { text-align: center; padding: 2.5rem 0 1.5rem; }
    .hero h1 {
        font-size: 3rem; font-weight: 700; letter-spacing: -1px;
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #34d399 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero p { color: #64748b; font-size: 1rem; margin-top: 0.5rem; letter-spacing: 0.05em; text-transform: uppercase; font-size: 0.75rem; }

    /* Cards */
    .card {
        background: #0d1526;
        border: 1px solid #1e2d45;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }
    .card-glow {
        background: #0d1526;
        border: 1px solid #2563eb44;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 0 24px #2563eb18;
        margin-bottom: 1rem;
    }

    /* Metric overrides */
    [data-testid="stMetric"] {
        background: #0d1526;
        border: 1px solid #1e2d45;
        border-radius: 12px;
        padding: 1rem 1.25rem;
    }
    [data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
    [data-testid="stMetricValue"] { color: #f1f5f9 !important; font-size: 1.5rem !important; font-weight: 600 !important; }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* Sentiment badge */
    .badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.05em;
    }
    .badge-bullish { background: #052e16; color: #34d399; border: 1px solid #34d39944; }
    .badge-bearish { background: #2d0a0a; color: #f87171; border: 1px solid #f8717144; }
    .badge-neutral  { background: #1e1b2e; color: #a78bfa; border: 1px solid #a78bfa44; }

    /* Qubit pill */
    .qubit {
        background: #0f172a;
        border: 1px solid #2563eb55;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        color: #93c5fd;
        text-align: center;
        box-shadow: 0 0 12px #2563eb18;
    }

    /* Section label */
    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #475569;
        margin-bottom: 0.75rem;
    }

    /* Divider */
    hr { border-color: #1e2d45 !important; margin: 1.5rem 0 !important; }

    /* Input */
    .stTextInput input {
        background: #0d1526 !important;
        border: 1px solid #1e2d45 !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        font-size: 1rem !important;
        padding: 0.6rem 1rem !important;
    }
    .stTextInput input:focus { border-color: #2563eb !important; box-shadow: 0 0 0 3px #2563eb22 !important; }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        font-size: 0.95rem !important;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85 !important; }

    /* Progress bar */
    .stProgress > div > div { background: linear-gradient(90deg, #2563eb, #7c3aed) !important; border-radius: 999px !important; }
    .stProgress > div { background: #1e2d45 !important; border-radius: 999px !important; }

    /* Headline links */
    a { color: #60a5fa !important; text-decoration: none !important; }
    a:hover { color: #93c5fd !important; text-decoration: underline !important; }

    /* Caption */
    .stCaption { color: #475569 !important; }

    /* Spinner */
    .stSpinner > div { border-top-color: #2563eb !important; }

    /* Subheader */
    h2, h3 { color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>⚛ Quantum Finance</h1>
    <p>NLP Sentiment · Quantum Circuit Analysis · AI Peer Scoring</p>
</div>
""", unsafe_allow_html=True)

# ── Search ────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 3, 1])
with c2:
    ticker_input = st.text_input("", placeholder="Enter ticker — e.g. AAPL, TSLA, MSFT", max_chars=10, label_visibility="collapsed").upper().strip()
    search = st.button("⚛  Analyse", use_container_width=True)

if not (search and ticker_input):
    st.stop()

with st.spinner(f"Fetching data for {ticker_input}…"):
    try:
        res = requests.get(f"{API_URL}/analyze/{ticker_input}", timeout=180)
        res.raise_for_status()
        d = res.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
        st.stop()
    except Exception as e:
        st.error(f"Analysis failed: {e}")
        st.stop()

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 1: Stock Info ─────────────────────────────────────────────────────────
change_sign = "+" if d["change"] >= 0 else ""
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Ticker", d["ticker"])
    st.caption(d["company_name"])
with m2:
    st.metric("Price", f"${d['price']:.2f}", delta=f"{change_sign}{d['change']:.2f} ({change_sign}{d['change_percent']*100:.2f}%)")
with m3:
    st.metric("52W High / Low", f"${d['high_52w']:.2f} / ${d['low_52w']:.2f}")
with m4:
    st.metric("Market Cap", f"${d['market_cap']:,.0f}")

st.caption(f"**Sector:** {d['sector']}  ·  **Industry:** {d['industry']}")
st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 2: Sentiment + Headlines ─────────────────────────────────────────────
left, right = st.columns([1, 2], gap="large")

with left:
    st.markdown("<div class='section-label'>FinBERT Sentiment</div>", unsafe_allow_html=True)
    label = d["sentiment"]["label"]
    badge_cls = {"Bullish": "badge-bullish", "Bearish": "badge-bearish"}.get(label, "badge-neutral")
    st.markdown(f"<span class='badge {badge_cls}'>{label}</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.metric("Sentiment Score", f"{d['sentiment']['score']} / 100")

    fig_sent = go.Figure(go.Bar(
        x=["Positive", "Negative", "Neutral"],
        y=[d["sentiment"]["positive"], d["sentiment"]["negative"], d["sentiment"]["neutral"]],
        marker_color=["#34d399", "#f87171", "#a78bfa"],
        marker_line_width=0,
    ))
    fig_sent.update_layout(
        height=180, margin=dict(t=8, b=8, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", size=11),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False),
    )
    st.plotly_chart(fig_sent, use_container_width=True)

with right:
    st.markdown("<div class='section-label'>Latest Headlines</div>", unsafe_allow_html=True)
    for h in d["headlines"]:
        st.markdown(f"<div class='card' style='margin-bottom:0.5rem;padding:0.75rem 1rem;'>📰 <a href='{h['link']}' target='_blank'>{h['title']}</a><br><span style='color:#475569;font-size:0.78rem;'>{h['publisher']}</span></div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 3: Quantum Metrics ────────────────────────────────────────────────────
st.markdown("<div class='section-label'>⚛ Quantum Circuit Metrics</div>", unsafe_allow_html=True)
st.caption("Computed via RY gates, CNOT entanglement, and Born rule measurement")

qc1, qc2, qc3 = st.columns(3)
with qc1:
    st.metric("Entanglement Score", f"{d['quantum_metrics']['entanglement_score']} / 100")
    st.progress(d["quantum_metrics"]["entanglement_score"] / 100)
with qc2:
    st.metric("Superposition Stability", f"{d['quantum_metrics']['superposition_stability']}%")
    st.progress(d["quantum_metrics"]["superposition_stability"] / 100)
with qc3:
    risk = d["quantum_metrics"]["decoherence_risk"]
    icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(risk, "")
    st.metric("Decoherence Risk", f"{icon} {risk}")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-label'>Qubit States — Bloch Sphere</div>", unsafe_allow_html=True)
labels = ["Price Change", "Volume Ratio", "52W Position", "Sentiment"]
qb_cols = st.columns(4)
for i, (state, prob) in enumerate(zip(d["quantum_metrics"]["qubit_states"], d["quantum_metrics"]["probabilities"])):
    with qb_cols[i]:
        st.markdown(f"<div class='qubit'>q[{i}] = {state}</div>", unsafe_allow_html=True)
        st.caption(f"{labels[i]}: P(|1⟩) = {prob}")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 4: Peers + Top Alternative ───────────────────────────────────────────
peer_col, alt_col = st.columns([2, 1], gap="large")

with peer_col:
    st.markdown("<div class='section-label'>Sector Peer Ranking</div>", unsafe_allow_html=True)
    peers_data = [{"Ticker": d["ticker"], "Quantum Score": d["sentiment"]["score"], "Main": True}]
    for p in d["peers"]:
        peers_data.append({"Ticker": p["ticker"], "Quantum Score": p["quantum_score"], "Main": False})
    peers_df = pd.DataFrame(peers_data).sort_values("Quantum Score", ascending=True)

    fig_peers = go.Figure(go.Bar(
        x=peers_df["Quantum Score"],
        y=peers_df["Ticker"],
        orientation="h",
        marker_color=["#2563eb" if m else "#1e2d45" for m in peers_df["Main"]],
        marker_line_width=0,
    ))
    fig_peers.update_layout(
        height=260, margin=dict(t=8, b=8, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", size=12),
        xaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
    )
    st.plotly_chart(fig_peers, use_container_width=True)

with alt_col:
    st.markdown("<div class='section-label'>Top Alternative Pick</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='card-glow'>
        <div style='font-size:2rem;font-weight:700;background:linear-gradient(135deg,#60a5fa,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>{d['top_alternative']['ticker']}</div>
        <div style='color:#94a3b8;font-size:0.88rem;margin-top:0.5rem;line-height:1.6;'>{d['top_alternative']['reasoning']}</div>
    </div>
    """, unsafe_allow_html=True)
