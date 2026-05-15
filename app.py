import streamlit as st
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
from duckduckgo_search import DDGS
import pandas as pd
import os
import json
import re
import time

# ================= PAGE CONFIG ================= #

st.set_page_config(
    page_title="CaseMind AI",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= LOAD ENV ================= #

load_dotenv()
client = InferenceClient(token=os.getenv("HF_TOKEN"))

# ================= JSON FIXER ================= #

def fix_json(text):
    text = text.replace("```json", "").replace("```", "")
    text = text.replace("%", "")
    text = re.sub(r'[\x00-\x1F]+', ' ', text)
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)

    # Extract outermost JSON block
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        text = match.group(0)

    # Try to close truncated JSON
    try:
        json.loads(text)
        return text
    except:
        if text.count('"') % 2 != 0:
            text += '"'
        text += ']' * max(0, text.count('[') - text.count(']'))
        text += '}' * max(0, text.count('{') - text.count('}'))

    return text.strip()

def get_live_company_context(company_name):

    search_query = f"{company_name} latest news revenue funding products competitors market"

    snippets = []

    try:
        with DDGS() as ddgs:

            results = ddgs.text(
                search_query,
                max_results=8
            )

            for r in results:

                title = r.get("title", "")
                body = r.get("body", "")

                snippets.append(f"TITLE: {title}\nBODY: {body}")

    except Exception as e:
        return ""

    return "\n\n".join(snippets)
# ================= GLOBAL CSS ================= #

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap" rel="stylesheet">

<style>

/* ── ROOT TOKENS ── */
:root {
    --bg:        #06070D;
    --surface:   #0E1018;
    --border:    rgba(255,255,255,0.07);
    --accent1:   #00E5FF;
    --accent2:   #7B61FF;
    --accent3:   #FF4DCA;
    --text:      #E8EAF0;
    --muted:     #6B7280;
    --card-bg:   rgba(255,255,255,0.034);
    --glow1:     rgba(0,229,255,0.15);
    --glow2:     rgba(123,97,255,0.15);
}

/* ── BASE ── */
html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── ANIMATED BACKGROUND MESH ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 10% 20%, var(--glow2) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 80%, var(--glow1) 0%, transparent 60%),
        radial-gradient(ellipse 40% 30% at 50% 50%, rgba(255,77,202,0.05) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--accent2); border-radius: 4px; }

/* ── HERO ── */
.hero {
    position: relative;
    padding: 80px 60px 70px;
    margin-bottom: 52px;
    border-radius: 32px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    overflow: hidden;
    text-align: center;
}

.hero::before {
    content: '';
    position: absolute;
    top: -60px; left: 50%; transform: translateX(-50%);
    width: 600px; height: 200px;
    background: radial-gradient(ellipse, rgba(123,97,255,0.3) 0%, transparent 70%);
    pointer-events: none;
}

.hero-eyebrow {
    display: inline-block;
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--accent1);
    background: rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.2);
    padding: 6px 18px;
    border-radius: 999px;
    margin-bottom: 24px;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(52px, 7vw, 88px);
    font-weight: 800;
    line-height: 1.02;
    color: #fff;
    margin: 0 0 18px;
    letter-spacing: -0.02em;
}

.hero-title span {
    background: linear-gradient(90deg, var(--accent1), var(--accent2), var(--accent3));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: 18px;
    font-weight: 300;
    color: var(--muted);
    max-width: 540px;
    margin: 0 auto 36px;
    line-height: 1.7;
}

.pill-row { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }

.pill {
    font-size: 13px;
    font-weight: 500;
    padding: 7px 18px;
    border-radius: 999px;
    border: 1px solid var(--border);
    color: var(--muted);
    background: rgba(255,255,255,0.03);
    letter-spacing: 0.01em;
}

/* ── CARD ── */
.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}

.card-label {
    font-family: 'Syne', sans-serif;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent1);
    margin-bottom: 6px;
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #fff;
    margin: 0 0 24px;
}

/* ── BULLET ITEMS ── */
.insight-item {
    display: flex;
    gap: 14px;
    align-items: flex-start;
    padding: 14px 0;
    border-bottom: 1px solid var(--border);
    font-size: 15px;
    line-height: 1.65;
    color: var(--text);
}

.insight-item:last-child { border-bottom: none; }

.insight-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent1);
    flex-shrink: 0;
    margin-top: 8px;
}

/* ── KPI CARDS ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-top: 28px;
}

.kpi-card {
    background: rgba(123,97,255,0.07);
    border: 1px solid rgba(123,97,255,0.2);
    border-radius: 18px;
    padding: 24px 20px;
    text-align: center;
}

.kpi-val {
    font-family: 'Syne', sans-serif;
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent1), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin-bottom: 8px;
}

.kpi-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--muted);
    line-height: 1.4;
}

/* ── SWOT ── */
.swot-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 16px;
    margin-bottom: 28px;
}

.swot-cell {
    border-radius: 20px;
    padding: 28px;
    min-height: 260px;
}

.swot-cell.s { background: rgba(0,229,255,0.05); border: 1px solid rgba(0,229,255,0.15); }
.swot-cell.w { background: rgba(255,77,202,0.05); border: 1px solid rgba(255,77,202,0.15); }
.swot-cell.o { background: rgba(123,97,255,0.05); border: 1px solid rgba(123,97,255,0.2); }
.swot-cell.t { background: rgba(255,160,0,0.05); border: 1px solid rgba(255,160,0,0.15); }

.swot-head {
    font-family: 'Syne', sans-serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 18px;
}

.swot-cell.s .swot-head { color: var(--accent1); }
.swot-cell.w .swot-head { color: var(--accent3); }
.swot-cell.o .swot-head { color: var(--accent2); }
.swot-cell.t .swot-head { color: #FFA000; }

.swot-item {
    font-size: 14px;
    color: var(--text);
    line-height: 1.6;
    margin-bottom: 10px;
    padding-left: 14px;
    position: relative;
    opacity: 0.85;
}

.swot-item::before {
    content: '›';
    position: absolute; left: 0;
    font-weight: 700;
    opacity: 0.6;
}

/* ── COMPETITOR TABLE ── */
.comp-row {
    display: grid;
    grid-template-columns: 1fr 2fr 2fr;
    gap: 16px;
    padding: 18px 20px;
    border-radius: 14px;
    margin-bottom: 10px;
    background: rgba(255,255,255,0.025);
    border: 1px solid var(--border);
    align-items: center;
    font-size: 14px;
    color: var(--text);
}

.comp-row:hover { border-color: rgba(123,97,255,0.35); }

.comp-name {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 15px;
    color: #fff;
}

.comp-adv {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.comp-tag {
    font-size: 12px;
    padding: 4px 10px;
    border-radius: 6px;
    background: rgba(123,97,255,0.1);
    border: 1px solid rgba(123,97,255,0.2);
    color: var(--accent2);
    width: fit-content;
}

/* ── MARKET POSITIONING ── */
.pos-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
}

.pos-grid-col {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.pos-item {
    border-radius: 16px;
    padding: 22px 20px;
    border: 1px solid var(--border);
    background: rgba(255,255,255,0.025);
}

.pos-key {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
}

.pos-val {
    font-family: 'Syne', sans-serif;
    font-size: 16px;
    font-weight: 600;
    color: var(--accent1);
}

/* ── FINAL INSIGHT ── */
.final-box {
    position: relative;
    background: linear-gradient(135deg, rgba(123,97,255,0.08), rgba(0,229,255,0.05));
    border: 1px solid rgba(123,97,255,0.25);
    border-radius: 24px;
    padding: 40px;
    overflow: hidden;
}

.final-box::before {
    content: '⬡';
    position: absolute;
    top: -10px; right: 24px;
    font-size: 120px;
    opacity: 0.04;
    color: var(--accent2);
    line-height: 1;
}

.final-text {
    font-size: 17px;
    line-height: 1.8;
    color: var(--text);
    max-width: 900px;
}

/* ── INPUT ── */
.stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    color: white !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 16px !important;
    padding: 14px 18px !important;
    caret-color: var(--accent1) !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent2) !important;
    box-shadow: 0 0 0 3px rgba(123,97,255,0.15) !important;
}

.stTextInput label {
    font-family: 'Syne', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* ── BUTTON ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent2), var(--accent1)) !important;
    color: #06070D !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: 0.05em !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 14px 36px !important;
    box-shadow: 0 8px 32px rgba(0,229,255,0.2) !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    box-shadow: 0 12px 40px rgba(0,229,255,0.35) !important;
    transform: translateY(-2px) !important;
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: var(--accent1) !important; }

/* ── SECTION DIVIDER ── */
.section-sep {
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 40px 0 32px;
}

.section-sep-line {
    flex: 1;
    height: 1px;
    background: var(--border);
}

.section-sep-label {
    font-family: 'Syne', sans-serif;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
}

/* ── OVERVIEW BOX ── */
.overview-text {
    font-size: 16px;
    font-weight: 300;
    line-height: 1.85;
    color: var(--text);
    opacity: 0.9;
}

/* ── WARNING / ERROR ── */
.stAlert { border-radius: 14px !important; }

/* Plotly chart container */
.js-plotly-plot { border-radius: 16px; }

</style>
""", unsafe_allow_html=True)

# ================= HERO ================= #

st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">AI-Powered Business Intelligence</div>
    <div class="hero-title">Case<span>Mind</span> AI</div>
    <div class="hero-sub">
        Deep consulting-grade analysis for any company or product — powered by frontier AI.
    </div>
    <div class="pill-row">
        <div class="pill">Product Strategy</div>
        <div class="pill">Competitive Intelligence</div>
        <div class="pill">Market Research</div>
        <div class="pill">SWOT Analysis</div>
        <div class="pill">Revenue Modeling</div>
        <div class="pill">PM Recommendations</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================= INPUT AREA ================= #

col_in, col_btn = st.columns([4, 1])

with col_in:
    company_name = st.text_input(
        "Company or Product Name",
        placeholder="e.g. Notion, Zepto, Paytm India, Shopify..."
    )

with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    run = st.button("⬡ Analyse", use_container_width=True)

st.caption("Tip: Add industry or geography for niche companies — e.g. 'ABC Logistics Dubai' or 'XYZ EdTech India'.")

# ================= PLOTLY THEME ================= #

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#E8EAF0"),
    margin=dict(l=20, r=20, t=40, b=20),
)

ACCENT_COLORS = ["#00E5FF", "#7B61FF", "#FF4DCA", "#FFA000", "#00E676", "#FF6B35"]

# ================= GENERATE ================= #

if run:
    if not company_name.strip():
        st.warning("Please enter a company or product name.")
    else:
        with st.spinner("⬡ Running deep analysis…"):
            live_context = get_live_company_context(company_name)
        
            prompt = f"""You are a business analyst. Return ONLY valid JSON, no markdown, no extra text.
                        - VERY IMPOSTANT Competitors must be DIRECT competitors in the SAME industry and market segment only.
                        - Use realistic insights and latest search on the web, news articles and the company website and social media platform for latest numbers for revenue also and if not available give the ans as not publically available.
                        - Use company-specific KPIs and also one line each how did you calculate those data 
                        - but MAJOR THING WHICH YOU NEED TO BE CAREFULL ABOUT IS DON'T PUT ANY ASSUMTION AND TRY TO PUT ASSUMED NUMBERS IF NOT AVAILABLE PUBLICALLY JUST SAY NOT AVAILABLE
                        - Generate a detailed consulting-style business analysis for:
Company: {company_name}
                        - You are given REAL live web search snippets about a company.
                        - Use these snippets heavily while generating insights
                        - LIVE SEARCH CONTEXT:

{live_context}


Return this exact JSON with real, specific data:
{{
"company_overview":"2 sentence summary with founding year and market position.",
"business_model":["value proposition","operational model","monetisation approach"],
"target_audience":"primary and secondary customer segments.",
"revenue_model":["primary stream","secondary stream","emerging stream"],
"revenue_breakdown":{{"Subscriptions":55,"Advertising":25,"Partnerships":15,"Other":5}},
"strengths":["strength 1","strength 2","strength 3","strength 4","strength 5"],
"weaknesses":["weakness 1","weakness 2","weakness 3","weakness 4","weakness 5"],
"opportunities":["opportunity 1","opportunity 2","opportunity 3","opportunity 4","opportunity 5"],
"threats":["threat 1","threat 2","threat 3","threat 4","threat 5"],
"pm_recommendations":["recommendation 1","recommendation 2","recommendation 3","recommendation 4","recommendation 5"],
"scores":{{"Product-Market Fit":8,"Brand Strength":7,"Tech Moat":6,"Customer Retention":8,"Revenue Diversification":5}},
"competitor_benchmarking":[{{"competitor":"Name","advantage_1":"advantage","advantage_2":"advantage"}},{{"competitor":"Name","advantage_1":"advantage","advantage_2":"advantage"}},{{"competitor":"Name","advantage_1":"advantage","advantage_2":"advantage"}}],
"market_positioning":{{"pricing_position":"Mid-market with context","market_type":"B2C platform","innovation_position":"Fast-follower"}},
"key_metrics":{{"Monthly Active Users":"400M+","Revenue":"13B USD","Market Share":"31 percent"}},
"final_insight":"3 sentence executive verdict on strengths, risks, and top strategic priority."
}}

Replace ALL placeholder values with REAL data about {company_name}. Return only the JSON object."""

            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="meta-llama/Llama-3.1-8B-Instruct",
                max_tokens=4096,
                temperature=0.15
            )

            raw = response.choices[0].message.content
            cleaned = raw.replace("```json", "").replace("```", "")
            fixed = fix_json(cleaned)

            try:
                data = json.loads(fixed)
            except Exception as e:
                st.error(f"JSON parse error: {e}")
                st.code(fixed)
                st.stop()

        # ── SECTION HELPER ──
        def sep(label):
            st.markdown(f"""
            <div class="section-sep">
                <div class="section-sep-line"></div>
                <div class="section-sep-label">{label}</div>
                <div class="section-sep-line"></div>
            </div>
            """, unsafe_allow_html=True)

        def card_open(label, title):
            st.markdown(f"""
            <div class="card">
                <div class="card-label">{label}</div>
                <div class="card-title">{title}</div>
            """, unsafe_allow_html=True)

        def card_close():
            st.markdown("</div>", unsafe_allow_html=True)

        # ── OVERVIEW ──
        sep("Company Overview")
        st.markdown(f"""
        <div class="card">
            <div class="card-label">Executive Summary</div>
            <div class="card-title">{company_name}</div>
            <div class="overview-text">{data.get("company_overview","")}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── KEY METRICS (if available) ──
        km = data.get("key_metrics", {})
        if km:
            items_html = ""
            for label, val in km.items():
                items_html += f"""
                <div class="kpi-card">
                    <div class="kpi-val">{val}</div>
                    <div class="kpi-label">{label}</div>
                </div>"""
            st.markdown(f'<div class="kpi-grid">{items_html}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        # ── BUSINESS MODEL + TARGET AUDIENCE ──
        sep("Business Model & Audience")
        col_bm, col_ta = st.columns([1, 1])

        with col_bm:
            items = "".join(
                f'<div class="insight-item"><div class="insight-dot"></div><div>{i}</div></div>'
                for i in data.get("business_model", [])
            )
            st.markdown(f"""
            <div class="card" style="height:100%">
                <div class="card-label">How They Operate</div>
                <div class="card-title">Business Model</div>
                {items}
            </div>""", unsafe_allow_html=True)

        with col_ta:
            st.markdown(f"""
            <div class="card" style="height:100%">
                <div class="card-label">Who They Serve</div>
                <div class="card-title">Target Audience</div>
                <div style="font-size:15px;line-height:1.8;color:var(--text);opacity:0.9">{data.get("target_audience","")}</div>
            </div>""", unsafe_allow_html=True)

        # ── REVENUE ──
        sep("Revenue Intelligence")
        col_rm, col_pie = st.columns([1, 1.2])

        with col_rm:
            items = "".join(
                f'<div class="insight-item"><div class="insight-dot"></div><div>{i}</div></div>'
                for i in data.get("revenue_model", [])
            )
            st.markdown(f"""
            <div class="card" style="height:100%">
                <div class="card-label">Monetisation</div>
                <div class="card-title">Revenue Model</div>
                {items}
            </div>""", unsafe_allow_html=True)

        with col_pie:
            rev = data.get("revenue_breakdown", {})
            if rev:
                rev_df = pd.DataFrame({
                    "Stream": list(rev.keys()),
                    "Pct": list(rev.values())
                })
                fig_pie = px.pie(
                    rev_df, names="Stream", values="Pct",
                    hole=0.52, color_discrete_sequence=ACCENT_COLORS
                )
                fig_pie.update_traces(
                    textfont=dict(family="DM Sans", size=13),
                    marker=dict(line=dict(color="#06070D", width=2))
                )
                fig_pie.update_layout(
                    **PLOTLY_LAYOUT,
                    title=dict(text="Revenue Breakdown", font=dict(size=15, family="Syne")),
                    legend=dict(orientation="v", x=1.02, y=0.5),
                    height=380
                )
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

        # ── SWOT ──
        sep("SWOT Analysis")

        def swot_items(lst):
            return "".join(f'<div class="swot-item">{i}</div>' for i in lst)

        st.markdown(f"""
        <div class="swot-grid">
            <div class="swot-cell s">
                <div class="swot-head">⬡ Strengths</div>
                {swot_items(data.get("strengths", []))}
            </div>
            <div class="swot-cell w">
                <div class="swot-head">⬡ Weaknesses</div>
                {swot_items(data.get("weaknesses", []))}
            </div>
            <div class="swot-cell o">
                <div class="swot-head">⬡ Opportunities</div>
                {swot_items(data.get("opportunities", []))}
            </div>
            <div class="swot-cell t">
                <div class="swot-head">⬡ Threats</div>
                {swot_items(data.get("threats", []))}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── KPI RADAR + BAR ──
        sep("Strategic KPI Scoring")
        scores = data.get("scores", {})

        if scores:
            col_bar, col_radar = st.columns([1.2, 1])

            with col_bar:
                sc_df = pd.DataFrame({
                    "KPI": list(scores.keys()),
                    "Score": list(scores.values())
                })
                fig_bar = px.bar(
                    sc_df, x="KPI", y="Score", text="Score",
                    color="Score",
                    color_continuous_scale=[[0,"#7B61FF"],[0.5,"#00E5FF"],[1,"#00E676"]],
                    range_color=[0, 10]
                )
                fig_bar.update_traces(
                    texttemplate="%{text}/10",
                    textposition="outside",
                    marker_line_width=0,
                )
                fig_bar.update_layout(
                    **PLOTLY_LAYOUT,
                    title=dict(text="KPI Scores (out of 10)", font=dict(size=15, family="Syne")),
                    yaxis=dict(range=[0, 11], showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                    xaxis=dict(showgrid=False),
                    coloraxis_showscale=False,
                    height=360,
                    bargap=0.35
                )
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            with col_radar:
                cats = list(scores.keys()) + [list(scores.keys())[0]]
                vals = list(scores.values()) + [list(scores.values())[0]]
                fig_radar = go.Figure(go.Scatterpolar(
                    r=vals, theta=cats,
                    fill="toself",
                    line=dict(color="#00E5FF", width=2),
                    fillcolor="rgba(0,229,255,0.08)"
                ))
                fig_radar.update_layout(
                    **PLOTLY_LAYOUT,
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(range=[0,10], showticklabels=True, tickfont=dict(size=10), gridcolor="rgba(255,255,255,0.07)"),
                        angularaxis=dict(gridcolor="rgba(255,255,255,0.07)")
                    ),
                    title=dict(text="Capability Radar", font=dict(size=15, family="Syne")),
                    height=360
                )
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            # KPI metric cards
            kpi_keys = list(scores.keys())
            kpi_vals = list(scores.values())
            cards_html = ""
            for k, v in zip(kpi_keys, kpi_vals):
                cards_html += f"""
                <div class="kpi-card">
                    <div class="kpi-val">{v}</div>
                    <div class="kpi-label">{k}</div>
                </div>"""
            st.markdown(f'<div class="kpi-grid">{cards_html}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        # ── PM RECOMMENDATIONS ──
        sep("Product Management Recommendations")
        recs = data.get("pm_recommendations", [])
        st.markdown('<div class="card"><div class="card-label">Strategic Actions</div><div class="card-title">PM Recommendations</div>', unsafe_allow_html=True)
        for idx, r in enumerate(recs, 1):
            st.markdown(
                f'<div class="insight-item">' +
                f'<div style="font-family:Syne,sans-serif;font-size:22px;font-weight:800;color:var(--accent2);min-width:30px;flex-shrink:0">{idx}</div>' +
                f'<div style="font-size:15px;line-height:1.7;color:var(--text)">{r}</div>' +
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── COMPETITORS ──
        sep("Competitive Landscape")
        comps = data.get("competitor_benchmarking", [])
        header = """
        <div class="comp-row" style="border-color:transparent;background:transparent;opacity:0.5;font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;">
            <div>Competitor</div>
            <div>Key Advantage 1</div>
            <div>Key Advantage 2</div>
        </div>"""
        rows = ""
        for c in comps:
            rows += f"""
            <div class="comp-row">
                <div class="comp-name">{c.get("competitor","")}</div>
                <div class="comp-adv"><span class="comp-tag">{c.get("advantage_1","")}</span></div>
                <div class="comp-adv"><span class="comp-tag" style="background:rgba(0,229,255,0.07);border-color:rgba(0,229,255,0.2);color:var(--accent1)">{c.get("advantage_2","")}</span></div>
            </div>"""
        st.markdown(f'<div class="card"><div class="card-label">Benchmarking</div><div class="card-title">Competitor Analysis</div>{header}{rows}</div>', unsafe_allow_html=True)

        # ── MARKET POSITIONING ──
        sep("Market Positioning")
        pos = data.get("market_positioning", {})
        st.markdown('<div class="card"><div class="card-label">Positioning</div><div class="card-title">Market Position</div><div class="pos-grid-col">', unsafe_allow_html=True)
        for pos_key, pos_label in [("pricing_position","Pricing Position"),("market_type","Market Type"),("innovation_position","Innovation Stance")]:
            val = pos.get(pos_key, "—")
            st.markdown(
                f'<div class="pos-item"><div class="pos-key">{pos_label}</div><div class="pos-val">{val}</div></div>',
                unsafe_allow_html=True
            )
        st.markdown('</div></div>', unsafe_allow_html=True)

        # ── FINAL INSIGHT ──
        sep("Executive Verdict")
        final_text = data.get("final_insight", "")
        st.markdown('<div class="final-box">', unsafe_allow_html=True)
        st.markdown('<div class="card-label" style="margin-bottom:12px">&#9649; Strategic Verdict</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="final-text">{final_text}</div>', unsafe_allow_html=True)
        st.markdown('</div><br>', unsafe_allow_html=True)
