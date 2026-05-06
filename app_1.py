import os
os.environ["NUMPY_EXPERIMENTAL_ARRAY_FUNCTION"] = "0"
import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  USER AUTHENTICATION & ROLES
# ─────────────────────────────────────────────
USERS = {
    "admin":  {"password": "admin123",  "role": "admin",  "name": "Administrator"},
    "viewer": {"password": "view123",   "role": "viewer", "name": "Viewer"},
    "hamza":  {"password": "hamza2024", "role": "admin",  "name": "Hamza"},
}

ROLE_PAGES = {
    "admin":  ["Overview", "Sales", "Customers", "Products", "Payments", "Reviews", "SQL Explorer"],
    "viewer": ["Overview", "Sales", "Customers", "Products", "Payments", "Reviews"],
}

def check_login(username: str, password: str):
    user = USERS.get(username.strip().lower())
    if user and user["password"] == password:
        return user
    return None

def logout():
    for key in ["authenticated", "username", "role", "user_name"]:
        st.session_state.pop(key, None)
    st.rerun()
    # Logout method

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SalesSphere",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# If you accidentally close the sidebar, click the ">" arrow in the top-left corner to reopen it.
# This code ensures it starts in the 'expanded' state.

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:          #080B0F;
    --bg2:         #0D1117;
    --surface:     #111820;
    --surface2:    #161E28;
    --card:        #1A2332;
    --border:      #1F2D3D;
    --border2:     #263545;
    --gold:        #E8C547;
    --gold2:       #F5D978;
    --gold-dim:    rgba(232,197,71,0.08);
    --gold-glow:   rgba(232,197,71,0.15);
    --teal:        #2DD4BF;
    --teal-dim:    rgba(45,212,191,0.08);
    --rose:        #FB7185;
    --rose-dim:    rgba(251,113,133,0.08);
    --sky:         #38BDF8;
    --sky-dim:     rgba(56,189,248,0.08);
    --violet:      #A78BFA;
    --text:        #E2E8F0;
    --text2:       #94A3B8;
    --text3:       #64748B;
    --radius:      12px;
    --radius-lg:   18px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background: var(--bg);
    color: var(--text);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
.stApp { background: var(--bg); }

section[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
    width: 260px !important;
}
section[data-testid="stSidebar"] > div {
    padding: 0 !important;
    background: var(--bg2) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

.stButton > button {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    padding: 10px 12px !important;
    text-align: left !important;
    width: 100% !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: var(--text2) !important;
    transition: all 0.15s !important;
    margin-bottom: 2px !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}
.stButton > button:hover {
    background: var(--surface) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}
.nav-btn-active .stButton > button {
    background: var(--gold-dim) !important;
    color: var(--gold) !important;
    border-color: rgba(232,197,71,0.2) !important;
    font-weight: 600 !important;
}

.stMultiSelect > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}
.stMultiSelect span {
    background: var(--gold-dim) !important;
    color: var(--gold) !important;
    border: 1px solid rgba(232,197,71,0.2) !important;
}

.stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    border-radius: 8px !important;
}
.stTextArea textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px var(--gold-dim) !important;
}

.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}
.stDataFrame th {
    background: var(--surface2) !important;
    color: var(--gold) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}
.stDataFrame td {
    font-size: 0.84rem !important;
    color: var(--text2) !important;
}

.stSuccess {
    background: rgba(45,212,191,0.1) !important;
    border: 1px solid rgba(45,212,191,0.3) !important;
    color: var(--teal) !important;
    border-radius: 8px !important;
}
.stAlert {
    background: rgba(251,113,133,0.1) !important;
    border: 1px solid rgba(251,113,133,0.3) !important;
    border-radius: 8px !important;
}

.main-wrapper {
    padding: 28px 32px 40px 32px;
    min-height: 100vh;
}

.page-header {
    margin-bottom: 32px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
}
.page-title {
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -0.02em;
    line-height: 1;
}
.page-subtitle {
    font-size: 0.85rem;
    color: var(--text3);
    margin-top: 6px;
    font-weight: 400;
}
.page-badge {
    background: var(--gold-dim);
    border: 1px solid rgba(232,197,71,0.25);
    color: var(--gold);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 20px;
}

.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}
.kpi-row-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}
.kpi {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
    cursor: default;
}
.kpi:hover {
    border-color: var(--border2);
    transform: translateY(-2px);
}
.kpi-accent-bar {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 999px;
}
.kpi-accent-bg {
    position: absolute;
    top: 0; right: 0;
    width: 80px; height: 80px;
    border-radius: 50%;
    opacity: 0.06;
    transform: translate(20px, -20px);
}
.kpi-icon-wrap {
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    margin-bottom: 14px;
}
.kpi-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text3);
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text);
    line-height: 1;
}
.kpi-sub {
    font-size: 0.75rem;
    color: var(--text3);
    margin-top: 8px;
    display: flex;
    align-items: center;
    gap: 5px;
}
.kpi-trend-up   { color: var(--teal); }
.kpi-trend-down { color: var(--rose); }

.sec {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text3);
    margin: 28px 0 14px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.sec::before {
    content: '';
    width: 14px; height: 2px;
    background: var(--gold);
    border-radius: 999px;
}

.chart-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px 20px 8px 20px;
    margin-bottom: 0;
}
.chart-title {
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text2);
    margin-bottom: 4px;
}
.chart-desc {
    font-size: 0.75rem;
    color: var(--text3);
    margin-bottom: 16px;
}

.sb-logo {
    padding: 24px 20px;
    margin-bottom: 10px;
}
.sb-logo-mark {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--gold), #C9A227);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 900; font-size: 1.2rem; color: #080B0F;
    margin-bottom: 12px;
}
.sb-logo-name {
    font-size: 1.15rem; font-weight: 800; color: var(--text);
    letter-spacing: -0.01em;
}
.sb-logo-sub {
    font-size: 0.72rem; color: var(--text3); font-weight: 400;
    margin-top: 2px;
}
.sb-nav-section {
    padding: 0 20px; margin-top: 10px; margin-bottom: 6px;
}
.sb-nav-label {
    font-size: 0.65rem; font-weight: 700; color: var(--text3);
    text-transform: uppercase; letter-spacing: 0.1em;
}
.sb-filter {
    padding: 24px 20px 0 20px;
}
.sb-filter-label {
    font-size: 0.65rem; font-weight: 700; color: var(--text3);
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 12px;
}
.sb-footer {
    position: fixed; bottom: 0; width: 260px;
    background: var(--bg2); border-top: 1px solid var(--border);
    padding: 20px;
}
.sb-footer-text {
    font-size: 0.7rem; color: var(--text2); line-height: 1.5;
}
.sb-footer-dot {
    display: inline-block; width: 6px; height: 6px;
    background: var(--teal); border-radius: 50%;
    margin-right: 8px; box-shadow: 0 0 8px var(--teal);
}

.sql-chip {
    display: inline-block; padding: 4px 10px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 6px; font-size: 0.72rem; color: var(--text2);
    margin-right: 6px; margin-bottom: 8px; cursor: pointer;
}
.sql-chip:hover {
    border-color: var(--gold); color: var(--gold);
}

.table-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius-lg); overflow: hidden;
}
.table-header {
    padding: 16px 20px; border-bottom: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: center;
}
.table-title {
    font-size: 0.85rem; font-weight: 700; color: var(--text);
}
.table-count {
    font-size: 0.72rem; color: var(--text3);
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text3); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOGIN WALL
# ─────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div style='text-align:center; margin-top: 10vh; margin-bottom: 20px;'>
        <div style='width:52px;height:52px;background:linear-gradient(135deg,#E8C547,#C9A227); border-radius:14px;display:inline-flex;align-items:center; justify-content:center;font-weight:900;font-size:1.5rem;color:#080B0F; margin-bottom:14px;'>S</div>
        <div style='font-size:1.4rem;font-weight:800;color:var(--text);'>SalesSphere</div>
        <div style='font-size:0.78rem;color:var(--text3);margin-top:4px;'>Sign in to your dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        st.markdown("<div style='background:var(--card); border:1px solid var(--border); border-radius:18px; padding:30px;'>", unsafe_allow_html=True)
        login_user = st.text_input("Username", placeholder="Username", key="login_user")
        login_pass = st.text_input("Password", type="password", placeholder="Password", key="login_pass")
        
        if st.button("Sign In", use_container_width=True, key="login_btn"):
            if not login_user.strip():
                st.error("⚠ Enter username")
            elif not login_pass.strip():
                st.error("⚠ Enter password")
            else:
                user = check_login(login_user, login_pass)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.username  = login_user.strip().lower()
                    st.session_state.role      = user["role"]
                    st.session_state.user_name = user["name"]
                    st.session_state.page      = "Overview"
                    st.rerun()
                else:
                    st.error("✘ Invalid credentials")
        
        st.markdown("""
        <div style='text-align:center;margin-top:14px;font-size:0.72rem;color:#64748B;'>
            Demo: <b style='color:#94A3B8'>admin / admin123</b>
        </div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
CHART_BG = "#1A2332"
GRID     = "#1F2D3D"
FONT_COL = "#94A3B8"
PALETTE  = ["#E8C547","#2DD4BF","#FB7185","#38BDF8","#A78BFA","#F97316","#34D399","#F472B6"]

def apply_theme(fig, height=340, legend=True):
    fig.update_layout(
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="Outfit", color=FONT_COL, size=12),
        height=height,
        margin=dict(l=12, r=12, t=28, b=12),
        legend=dict(
            bgcolor=CHART_BG,
            bordercolor=GRID,
            borderwidth=1,
            font=dict(size=11),
        ) if legend else dict(visible=False),
        xaxis=dict(
            gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID,
            tickfont=dict(size=11), title_font=dict(size=11)
        ),
        yaxis=dict(
            gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID,
            tickfont=dict(size=11), title_font=dict(size=11)
        ),
    )
    return fig

def chart(fig, height=340, legend=True):
    apply_theme(fig, height, legend)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ─────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────
@st.cache_resource
def get_connection():
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432,
            database="Hamza", user="postgres", password="Rizwana2020",
        )
        return conn
    except Exception as e:
        st.error(f"⚠ Database connection failed: {e}")
        st.stop()

@st.cache_data(ttl=300)
def q(sql):
    try:
        return pd.read_sql_query(sql, get_connection())
    except Exception as e:
        st.error(f"⚠ Query error: {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────
#  SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
ALL_PAGES = [
    ("◈", "Overview",          "Executive overview"),
    ("⟋", "Sales",             "Revenue & trends"),
    ("◎", "Customers",         "Customer analytics"),
    ("⬡", "Products",          "Product intelligence"),
    ("◇", "Payments",          "Payment insights"),
    ("★", "Reviews",           "Ratings & feedback"),
    ("⌗", "SQL Explorer",      "Custom queries"),
]

_allowed = ROLE_PAGES.get(st.session_state.get("role", "viewer"), [])
PAGES = [(icon, name, desc) for icon, name, desc in ALL_PAGES if name in _allowed]

if "page" not in st.session_state:
    st.session_state.page = "Overview"

with st.sidebar:
    st.markdown("""
    <div class='sb-logo'>
        <div class='sb-logo-mark'>S</div>
        <div class='sb-logo-name'>SalesSphere</div>
        <div class='sb-logo-sub'>Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sb-nav-section'><div class='sb-nav-label'>Navigation</div></div>", unsafe_allow_html=True)

    for icon, name, desc in PAGES:
        active_class = "nav-btn-active" if st.session_state.page == name else ""
        with st.container():
            if active_class:
                st.markdown(f'<div class="{active_class}" style="margin-bottom:2px;">', unsafe_allow_html=True)
            if st.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True):
                st.session_state.page = name
                st.rerun()
            if active_class:
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='sb-filter'><div class='sb-filter-label'>Filter by Year</div></div>", unsafe_allow_html=True)
    year_filter = st.multiselect("Year", [2022, 2023, 2024], default=[2022, 2023, 2024], label_visibility="collapsed")
    years_sql = "(" + ",".join(str(y) for y in year_filter) + ")" if year_filter else "(2022,2023,2024)"

    st.markdown(f"""
    <div class='sb-footer'>
        <div class='sb-footer-text'><span class='sb-footer-dot'></span>Live connection<br><span style='opacity:0.5'>PostgreSQL · Streamlit · Plotly</span></div>
        <div style='margin-top:10px;font-size:0.7rem;'>
            <span style='background:{"rgba(232,197,71,0.12)" if st.session_state.role=="admin" else "rgba(45,212,191,0.12)"}; color:{"#E8C547" if st.session_state.role=="admin" else "#2DD4BF"}; border:1px solid {"rgba(232,197,71,0.3)" if st.session_state.role=="admin" else "rgba(45,212,191,0.3)"}; padding:3px 10px; border-radius:20px; font-weight:600; letter-spacing:0.07em; text-transform:uppercase;'>{"⚙ Admin" if st.session_state.role=="admin" else "👁 Viewer"}</span>
            &nbsp;<span style='color:#64748B'>{st.session_state.get("user_name","")}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⬡  Sign Out", key="logout_btn", use_container_width=True):
        logout()

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def kpi_card(label, value, sub="", color="gold", icon="◈", trend=None):
    color_map = {
        "gold":   ("var(--gold)",   "var(--gold)"),
        "teal":   ("var(--teal)",   "var(--teal)"),
        "rose":   ("var(--rose)",   "var(--rose)"),
        "sky":    ("var(--sky)",    "var(--sky)"),
        "violet": ("var(--violet)", "var(--violet)"),
    }
    c, bg = color_map.get(color, color_map["gold"])
    trend_html = ""
    if trend == "up": trend_html = "<span class='kpi-trend-up'>↑</span>"
    elif trend == "down": trend_html = "<span class='kpi-trend-down'>↓</span>"
    return f"""
    <div class='kpi'>
        <div class='kpi-accent-bar' style='background:linear-gradient(90deg,{c},transparent)'></div>
        <div class='kpi-accent-bg' style='background:{bg}'></div>
        <div class='kpi-icon-wrap' style='background:rgba(0,0,0,0.3);color:{c}'>{icon}</div>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value'>{value}</div>
        <div class='kpi-sub'>{trend_html}{sub}</div>
    </div>"""

def sec(title):
    st.markdown(f"<div class='sec'>{title}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE DISPATCHING
# ─────────────────────────────────────────────
page = st.session_state.page

if page == "Overview":
    st.markdown("<div class='main-wrapper'><div class='page-header'><div><div class='page-title'>Executive Overview</div><div class='page-subtitle'>Real-time snapshot of business performance</div></div><div class='page-badge'>◈ Live Dashboard</div></div></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='padding:0 32px'>", unsafe_allow_html=True)
        kpis = q(f"SELECT COUNT(DISTINCT o.order_id) AS total_orders, ROUND(SUM(p.amount)::numeric,2) AS total_revenue, COUNT(DISTINCT o.customer_id) AS active_customers, ROUND(AVG(p.amount)::numeric,2) AS avg_order_value FROM orders o JOIN payments p ON o.order_id=p.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql}")
        if not kpis.empty:
            r = kpis.iloc[0]
            revenue_val = f"₨ {r['total_revenue']/1e6:.2f}M"
            orders_val = f"{int(r['total_orders']):,}"
            customers_val = f"{int(r['active_customers']):,}"
            aov_val = f"₨ {r['avg_order_value']:,.0f}"
            st.markdown(f"<div class='kpi-row'>{kpi_card('Total Revenue', revenue_val, 'Across all delivered orders', 'gold', '₨', 'up')}{kpi_card('Total Orders', orders_val, 'Completed transactions', 'teal', '⟋', 'up')}{kpi_card('Active Customers', customers_val, 'Unique buyers', 'sky', '◎', 'up')}{kpi_card('Avg Order Value', aov_val, 'Per transaction', 'violet', '◇')}</div>", unsafe_allow_html=True)
        
        sec("REVENUE TRENDS")
        col1, col2 = st.columns([3, 2], gap="medium")
        with col1:
            st.markdown("<div class='chart-card'><div class='chart-title'>Monthly Revenue</div><div class='chart-desc'>Cumulative revenue by month</div>", unsafe_allow_html=True)
            monthly = q(f"SELECT TO_CHAR(DATE_TRUNC('month',o.order_date),'Mon YY') AS month, DATE_TRUNC('month',o.order_date) AS mdt, ROUND(SUM(p.amount)::numeric,2) AS revenue, COUNT(o.order_id) AS orders FROM orders o JOIN payments p ON o.order_id=p.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY DATE_TRUNC('month',o.order_date) ORDER BY mdt")
            if not monthly.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["revenue"], mode="lines", line=dict(color="#E8C547", width=2.5), fill="tozeroy", fillcolor="rgba(232,197,71,0.06)", hovertemplate="<b>%{x}</b><br>₨ %{y:,.0f}<extra></extra>"))
                fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["revenue"], mode="markers", marker=dict(size=5, color="#E8C547", line=dict(width=2, color=CHART_BG)), showlegend=False, hovertemplate="<b>%{x}</b><br>₨ %{y:,.0f}<extra></extra>"))
                fig.update_layout(yaxis_tickprefix="₨ ", yaxis_tickformat=",.0f", xaxis_tickangle=-35, showlegend=False)
                chart(fig, 280)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='chart-card'><div class='chart-title'>Revenue by Category</div>", unsafe_allow_html=True)
            cat_rev = q(f"SELECT c.name AS category, ROUND(SUM(oi.unit_price*oi.quantity)::numeric,2) AS revenue FROM order_items oi JOIN products pr ON oi.product_id=pr.product_id JOIN categories c ON pr.category_id=c.category_id JOIN orders o ON oi.order_id=o.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY c.name ORDER BY revenue DESC")
            if not cat_rev.empty:
                fig = go.Figure(go.Pie(labels=cat_rev["category"], values=cat_rev["revenue"], hole=0.68, marker=dict(colors=PALETTE, line=dict(color=CHART_BG, width=2)), textinfo="none", hovertemplate="<b>%{label}</b><br>₨ %{value:,.0f}<br>%{percent}<extra></extra>"))
                fig.update_layout(annotations=[dict(text="Revenue", x=0.5, y=0.55, showarrow=False, font=dict(size=11, color="#94A3B8")), dict(text=f"₨{cat_rev['revenue'].sum()/1e6:.1f}M", x=0.5, y=0.42, showarrow=False, font=dict(size=16, color="#E8C547", family="Outfit"))], legend=dict(font=dict(size=10), x=1.02), margin=dict(l=0, r=80, t=10, b=10))
                chart(fig, 280, legend=True)
            st.markdown("</div>", unsafe_allow_html=True)

        sec("OPERATIONS SNAPSHOT")
        col3, col4 = st.columns(2, gap="medium")
        with col3:
            st.markdown("<div class='chart-card'><div class='chart-title'>Order Status</div>", unsafe_allow_html=True)
            status = q(f"SELECT order_status, COUNT(*) AS cnt FROM orders WHERE EXTRACT(YEAR FROM order_date) IN {years_sql} GROUP BY order_status ORDER BY cnt DESC")
            if not status.empty:
                STATUS_C = {"delivered": "#2DD4BF", "processing": "#E8C547", "pending": "#38BDF8", "cancelled": "#FB7185"}
                fig = go.Figure(go.Bar(x=status["order_status"], y=status["cnt"], marker_color=[STATUS_C.get(s, "#A78BFA") for s in status["order_status"]], marker_line_width=0, text=status["cnt"], textposition="outside", textfont=dict(color="#94A3B8", size=12), hovertemplate="<b>%{x}</b><br>%{y} orders<extra></extra>"))
                fig.update_layout(xaxis_title="", yaxis_title="", bargap=0.35, showlegend=False)
                chart(fig, 240)
            st.markdown("</div>", unsafe_allow_html=True)
        with col4:
            st.markdown("<div class='chart-card'><div class='chart-title'>Top 5 Products</div>", unsafe_allow_html=True)
            top5 = q(f"SELECT pr.name AS product, ROUND(SUM(oi.unit_price*oi.quantity)::numeric,2) AS revenue FROM order_items oi JOIN products pr ON oi.product_id=pr.product_id JOIN orders o ON oi.order_id=o.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY pr.name ORDER BY revenue DESC LIMIT 5")
            if not top5.empty:
                fig = go.Figure(go.Bar(y=top5["product"], x=top5["revenue"], orientation="h", marker=dict(color=top5["revenue"], colorscale=[[0, "#1F2D3D"], [1, "#E8C547"]], showscale=False, line_width=0), text=["₨ " + f"{v/1000:.0f}K" for v in top5["revenue"]], textposition="outside", textfont=dict(color="#94A3B8", size=11), hovertemplate="<b>%{y}</b><br>₨ %{x:,.0f}<extra></extra>"))
                fig.update_layout(yaxis_autorange="reversed", xaxis_tickprefix="₨ ", xaxis_tickformat=",.0f", showlegend=False)
                chart(fig, 240)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Sales":
    st.markdown("<div class='main-wrapper'><div class='page-header'><div><div class='page-title'>Sales & Revenue</div><div class='page-subtitle'>Deep-dive into revenue patterns and growth</div></div><div class='page-badge'>⟋ Analytics</div></div></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='padding:0 32px'>", unsafe_allow_html=True)
        sec("YEAR-OVER-YEAR COMPARISON")
        st.markdown("<div class='chart-card'><div class='chart-title'>Yearly Revenue Comparison</div>", unsafe_allow_html=True)
        yearly = q(f"SELECT EXTRACT(YEAR FROM o.order_date)::int AS year, TO_CHAR(DATE_TRUNC('month',o.order_date),'Mon') AS month_name, DATE_PART('month',o.order_date)::int AS month_num, ROUND(SUM(p.amount)::numeric,2) AS revenue FROM orders o JOIN payments p ON o.order_id=p.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY 1,2,3 ORDER BY 1,3")
        if not yearly.empty:
            fig = go.Figure()
            line_colors = ["#E8C547", "#2DD4BF", "#FB7185"]
            for i, yr in enumerate(sorted(yearly["year"].unique())):
                d = yearly[yearly["year"] == yr].sort_values("month_num")
                fig.add_trace(go.Scatter(x=d["month_name"], y=d["revenue"], name=str(yr), mode="lines+markers", line=dict(color=line_colors[i % 3], width=2.5), marker=dict(size=7, color=line_colors[i % 3], line=dict(width=2, color=CHART_BG)), hovertemplate=f"<b>{yr} %{{x}}</b><br>₨ %{{y:,.0f}}<extra></extra>"))
            fig.update_layout(yaxis_tickprefix="₨ ", yaxis_tickformat=",.0f", legend_title="Year")
            chart(fig, 320)
        st.markdown("</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="medium")
        sec("QUARTERLY & PAYMENT BREAKDOWN")
        with col1:
            st.markdown("<div class='chart-card'><div class='chart-title'>Quarterly Revenue</div>", unsafe_allow_html=True)
            quarterly = q(f"SELECT EXTRACT(YEAR FROM o.order_date)::int AS year, EXTRACT(QUARTER FROM o.order_date)::int AS quarter, ROUND(SUM(p.amount)::numeric,2) AS revenue FROM orders o JOIN payments p ON o.order_id=p.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY 1,2 ORDER BY 1,2")
            if not quarterly.empty:
                quarterly["label"] = quarterly["year"].astype(str) + " Q" + quarterly["quarter"].astype(str)
                fig = go.Figure(go.Bar(x=quarterly["label"], y=quarterly["revenue"], marker=dict(color=quarterly["revenue"], colorscale=[[0, "#1A2332"], [0.5, "#2DD4BF"], [1, "#E8C547"]], showscale=False, line_width=0), hovertemplate="<b>%{x}</b><br>₨ %{y:,.0f}<extra></extra>"))
                fig.update_layout(yaxis_tickprefix="₨ ", yaxis_tickformat=",.0f", bargap=0.3)
                chart(fig, 280)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='chart-card'><div class='chart-title'>Payment Methods</div>", unsafe_allow_html=True)
            pm = q(f"SELECT p.method, COUNT(*) AS cnt, ROUND(SUM(p.amount)::numeric,2) AS total FROM orders o JOIN payments p ON o.order_id=p.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY p.method ORDER BY total DESC")
            if not pm.empty:
                fig = go.Figure(go.Bar(x=pm["method"], y=pm["total"], marker=dict(color=PALETTE[:len(pm)], line_width=0), text=["₨ " + f"{v/1000:.0f}K" for v in pm["total"]], textposition="outside", textfont=dict(size=11, color="#94A3B8"), hovertemplate="<b>%{x}</b><br>₨ %{y:,.0f}<extra></extra>"))
                fig.update_layout(yaxis_tickprefix="₨ ", yaxis_tickformat=",.0f", bargap=0.35, showlegend=False)
                chart(fig, 280)
            st.markdown("</div>", unsafe_allow_html=True)

        sec("REVENUE HEATMAP")
        st.markdown("<div class='chart-card'><div class='chart-title'>Monthly Revenue Heatmap — Month × Year</div>", unsafe_allow_html=True)
        heat = q(f"SELECT EXTRACT(YEAR FROM o.order_date)::int AS year, EXTRACT(MONTH FROM o.order_date)::int AS month, ROUND(SUM(p.amount)::numeric,2) AS revenue FROM orders o JOIN payments p ON o.order_id=p.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY 1,2")
        if not heat.empty:
            pivot = heat.pivot(index="year", columns="month", values="revenue").fillna(0)
            months_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            pivot.columns = [months_names[c-1] for c in pivot.columns if c <= len(months_names)]
            fig = go.Figure(go.Heatmap(z=pivot.values, x=pivot.columns.tolist(), y=[str(y) for y in pivot.index], colorscale=[[0, "#111820"], [0.4, "#1A3A4A"], [0.7, "#2DD4BF"], [1, "#E8C547"]], hovertemplate="<b>%{y} %{x}</b><br>₨ %{z:,.0f}<extra></extra>", showscale=True, colorbar=dict(tickfont=dict(color="#64748B", size=10), outlinecolor=GRID, outlinewidth=1)))
            fig.update_layout(height=180, margin=dict(l=12, r=60, t=10, b=12))
            apply_theme(fig, 180)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Customers":
    st.markdown("<div class='main-wrapper'><div class='page-header'><div><div class='page-title'>Customer Analytics</div><div class='page-subtitle'>Understand your best customers and their behaviour</div></div><div class='page-badge'>◎ Intelligence</div></div></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='padding:0 32px'>", unsafe_allow_html=True)
        top_cust = q(f"SELECT cu.name, COUNT(DISTINCT o.order_id) AS orders, ROUND(SUM(p.amount)::numeric,2) AS revenue FROM customers cu JOIN orders o ON cu.customer_id=o.customer_id JOIN payments p ON o.order_id=p.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY cu.name ORDER BY revenue DESC LIMIT 10")
        col1, col2 = st.columns(2, gap="medium")
        sec("TOP CUSTOMERS")
        with col1:
            st.markdown("<div class='chart-card'><div class='chart-title'>Top 10 Customers by Revenue</div>", unsafe_allow_html=True)
            if not top_cust.empty:
                fig = go.Figure(go.Bar(y=top_cust["name"], x=top_cust["revenue"], orientation="h", marker=dict(color=top_cust["revenue"], colorscale=[[0, "#1A2332"], [1, "#E8C547"]], showscale=False, line_width=0), text=["₨ " + f"{v/1000:.0f}K" for v in top_cust["revenue"]], textposition="outside", textfont=dict(size=11, color="#94A3B8"), hovertemplate="<b>%{y}</b><br>₨ %{x:,.0f}<extra></extra>"))
                fig.update_layout(yaxis_autorange="reversed", xaxis_tickprefix="₨ ", xaxis_tickformat=",.0f", showlegend=False)
                chart(fig, 360)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='chart-card'><div class='chart-title'>New Customer Registrations</div>", unsafe_allow_html=True)
            reg = q(f"SELECT TO_CHAR(DATE_TRUNC('month',registered_on),'Mon YY') AS month, DATE_TRUNC('month',registered_on) AS mdt, COUNT(*) AS new_customers FROM customers WHERE EXTRACT(YEAR FROM registered_on) IN {years_sql} GROUP BY DATE_TRUNC('month',registered_on) ORDER BY mdt")
            if not reg.empty:
                fig = go.Figure(go.Bar(x=reg["month"], y=reg["new_customers"], marker=dict(color=reg["new_customers"], colorscale=[[0, "#1A3A4A"], [1, "#2DD4BF"]], showscale=False, line_width=0), hovertemplate="<b>%{x}</b><br>%{y} new customers<extra></extra>"))
                fig.update_layout(xaxis_tickangle=-35, yaxis_title="", bargap=0.3)
                chart(fig, 360)
            st.markdown("</div>", unsafe_allow_html=True)
        sec("SPEND DISTRIBUTION")
        st.markdown("<div class='chart-card'><div class='chart-title'>Customer Order Frequency vs Total Spend</div>", unsafe_allow_html=True)
        freq = q(f"SELECT cu.name, COUNT(DISTINCT o.order_id) AS order_count, ROUND(SUM(p.amount)::numeric,2) AS total_spent FROM customers cu JOIN orders o ON cu.customer_id=o.customer_id JOIN payments p ON o.order_id=p.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY cu.name")
        if not freq.empty:
            fig = px.scatter(freq, x="order_count", y="total_spent", hover_name="name", size="total_spent", size_max=30, color="total_spent", color_continuous_scale=[[0, "#1A2332"], [0.4, "#38BDF8"], [0.7, "#2DD4BF"], [1, "#E8C547"]], labels={"order_count": "Number of Orders", "total_spent": "Total Spent (₨)"})
            fig.update_traces(marker=dict(line=dict(width=1, color=CHART_BG), opacity=0.85))
            fig.update_coloraxes(showscale=False)
            fig.update_layout(yaxis_tickprefix="₨ ", yaxis_tickformat=",.0f")
            chart(fig, 320)
        st.markdown("</div>", unsafe_allow_html=True)
        sec("CUSTOMER LEADERBOARD")
        st.markdown("<div class='table-card'><div class='table-header'><div class='table-title'>Top Customers — Full Detail</div><div class='table-count'>Top 10</div></div></div>", unsafe_allow_html=True)
        if not top_cust.empty:
            display_df = top_cust.copy()
            display_df.columns = ["Customer", "Orders", "Revenue (₨)"]
            display_df["Revenue (₨)"] = display_df["Revenue (₨)"].apply(lambda x: f"₨ {x:,.0f}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Products":
    st.markdown("<div class='main-wrapper'><div class='page-header'><div><div class='page-title'>Product Intelligence</div><div class='page-subtitle'>Performance, category analysis and stock health</div></div><div class='page-badge'>⬡ Intelligence</div></div></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='padding:0 32px'>", unsafe_allow_html=True)
        cat = q(f"SELECT c.name AS category, ROUND(SUM(oi.unit_price*oi.quantity)::numeric,2) AS revenue, SUM(oi.quantity) AS units_sold FROM order_items oi JOIN products pr ON oi.product_id=pr.product_id JOIN categories c ON pr.category_id=c.category_id JOIN orders o ON oi.order_id=o.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY c.name ORDER BY revenue DESC")
        col1, col2 = st.columns(2, gap="medium")
        sec("CATEGORY PERFORMANCE")
        with col1:
            st.markdown("<div class='chart-card'><div class='chart-title'>Revenue by Category</div>", unsafe_allow_html=True)
            if not cat.empty:
                fig = go.Figure(go.Bar(x=cat["category"], y=cat["revenue"], marker=dict(color=PALETTE[:len(cat)], line_width=0), text=["₨ " + f"{v/1000:.0f}K" for v in cat["revenue"]], textposition="outside", textfont=dict(size=10, color="#94A3B8"), hovertemplate="<b>%{x}</b><br>₨ %{y:,.0f}<extra></extra>"))
                fig.update_layout(xaxis_tickangle=-30, yaxis_tickprefix="₨ ", yaxis_tickformat=",.0f", bargap=0.3, showlegend=False)
                chart(fig, 300)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='chart-card'><div class='chart-title'>Units Sold Share</div>", unsafe_allow_html=True)
            if not cat.empty:
                fig = go.Figure(go.Pie(labels=cat["category"], values=cat["units_sold"], hole=0.6, marker=dict(colors=PALETTE, line=dict(color=CHART_BG, width=2)), textinfo="label+percent", textfont=dict(size=10), hovertemplate="<b>%{label}</b><br>%{value:,} units<br>%{percent}<extra></extra>"))
                fig.update_layout(annotations=[dict(text=f"{cat['units_sold'].sum():,}<br>units", x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#E8C547"))], margin=dict(l=0, r=0, t=10, b=10), legend=dict(font=dict(size=10)))
                chart(fig, 300)
            st.markdown("</div>", unsafe_allow_html=True)
        sec("TOP PRODUCTS")
        st.markdown("<div class='chart-card'><div class='chart-title'>Top 15 Products — Revenue & Volume</div>", unsafe_allow_html=True)
        prod_detail = q(f"SELECT pr.name AS product, c.name AS category, SUM(oi.quantity) AS units_sold, ROUND(SUM(oi.unit_price*oi.quantity)::numeric,2) AS revenue FROM order_items oi JOIN products pr ON oi.product_id=pr.product_id JOIN categories c ON pr.category_id=c.category_id JOIN orders o ON oi.order_id=o.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY pr.name, c.name ORDER BY revenue DESC LIMIT 15")
        if not prod_detail.empty:
            fig = px.bar(prod_detail, x="product", y="revenue", color="category", color_discrete_sequence=PALETTE, hover_data={"units_sold": True}, labels={"revenue": "Revenue (₨)", "product": ""})
            fig.update_traces(marker_line_width=0)
            fig.update_layout(xaxis_tickangle=-30, yaxis_tickprefix="₨ ", yaxis_tickformat=",.0f", legend_title="Category", bargap=0.25)
            chart(fig, 340)
        st.markdown("</div>", unsafe_allow_html=True)
        sec("STOCK HEALTH")
        st.markdown("<div class='chart-card'><div class='chart-title'>Stock Levels — Low Stock Alert</div>", unsafe_allow_html=True)
        stock = q("SELECT name AS product, stock, CASE WHEN stock < 50 THEN 'Critical' WHEN stock < 100 THEN 'Low' ELSE 'Healthy' END AS status FROM products ORDER BY stock ASC LIMIT 20")
        if not stock.empty:
            STOCK_C = {"Critical": "#FB7185", "Low": "#E8C547", "Healthy": "#2DD4BF"}
            fig = go.Figure(go.Bar(y=stock["product"], x=stock["stock"], orientation="h", marker=dict(color=[STOCK_C[s] for s in stock["status"]], line_width=0), text=stock["stock"], textposition="outside", textfont=dict(size=10, color="#94A3B8"), hovertemplate="<b>%{y}</b><br>%{x} units<extra></extra>"))
            fig.update_layout(yaxis_autorange="reversed", xaxis_title="Units in Stock", showlegend=False)
            chart(fig, 460)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Payments":
    st.markdown("<div class='main-wrapper'><div class='page-header'><div><div class='page-title'>Payment Insights</div><div class='page-subtitle'>How customers pay and method performance</div></div><div class='page-badge'>◇ Finance</div></div></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='padding:0 32px'>", unsafe_allow_html=True)
        pay_kpi = q(f"SELECT COUNT(*) AS total_payments, ROUND(SUM(amount)::numeric,2) AS total_paid, ROUND(AVG(amount)::numeric,2) AS avg_payment FROM payments p JOIN orders o ON p.order_id=o.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql}")
        if not pay_kpi.empty:
            pk = pay_kpi.iloc[0]
            pay_total_val = f"{int(pk['total_payments']):,}"
            pay_collected_val = f"₨ {pk['total_paid']/1e6:.2f}M"
            pay_avg_val = f"₨ {pk['avg_payment']:,.0f}"
            st.markdown(f"<div class='kpi-row-3'>{kpi_card('Total Payments', pay_total_val, 'All transactions', 'gold', '◇')}{kpi_card('Total Collected', pay_collected_val, 'Revenue collected', 'teal', '₨', 'up')}{kpi_card('Avg Payment', pay_avg_val, 'Per transaction', 'sky', '~')}</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="medium")
        sec("PAYMENT METHOD ANALYSIS")
        pm = q(f"SELECT p.method, COUNT(*) AS transactions, ROUND(SUM(p.amount)::numeric,2) AS total FROM payments p JOIN orders o ON p.order_id=o.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY p.method ORDER BY total DESC")
        with col1:
            st.markdown("<div class='chart-card'><div class='chart-title'>Revenue Share by Method</div>", unsafe_allow_html=True)
            if not pm.empty:
                fig = go.Figure(go.Pie(labels=pm["method"], values=pm["total"], hole=0.65, marker=dict(colors=PALETTE, line=dict(color=CHART_BG, width=2)), textinfo="label+percent", textfont=dict(size=10), hovertemplate="<b>%{label}</b><br>₨ %{value:,.0f}<extra></extra>"))
                fig.update_layout(annotations=[dict(text="Methods", x=0.5, y=0.5, showarrow=False, font=dict(size=11, color="#64748B"))], margin=dict(l=0, r=60, t=10, b=10), legend=dict(font=dict(size=10), x=1.02))
                chart(fig, 300)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='chart-card'><div class='chart-title'>Average Payment per Method</div>", unsafe_allow_html=True)
            if not pm.empty:
                avgs = (pm["total"] / pm["transactions"]).round(0)
                fig = go.Figure(go.Bar(x=pm["method"], y=avgs, marker=dict(color=PALETTE[:len(pm)], line_width=0), text=["₨ " + f"{v:,.0f}" for v in avgs], textposition="outside", textfont=dict(size=11, color="#94A3B8"), hovertemplate="<b>%{x}</b><br>₨ %{y:,.0f}<extra></extra>"))
                fig.update_layout(yaxis_tickprefix="₨ ", yaxis_tickformat=",.0f", bargap=0.35, showlegend=False)
                chart(fig, 300)
            st.markdown("</div>", unsafe_allow_html=True)
        sec("PAYMENT TIMELINE")
        st.markdown("<div class='chart-card'><div class='chart-title'>Monthly Payment Volume by Method</div>", unsafe_allow_html=True)
        pt = q(f"SELECT TO_CHAR(DATE_TRUNC('month',p.paid_on),'Mon YY') AS month, DATE_TRUNC('month',p.paid_on) AS mdt, p.method, ROUND(SUM(p.amount)::numeric,2) AS total FROM payments p JOIN orders o ON p.order_id=o.order_id WHERE EXTRACT(YEAR FROM o.order_date) IN {years_sql} GROUP BY DATE_TRUNC('month',p.paid_on), p.method ORDER BY mdt")
        if not pt.empty:
            fig = px.area(pt, x="month", y="total", color="method", color_discrete_sequence=PALETTE, labels={"total": "Revenue (₨)", "month": ""})
            fig.update_traces(line_width=1.5)
            fig.update_layout(xaxis_tickangle=-35, yaxis_tickprefix="₨ ", yaxis_tickformat=",.0f", legend_title="Method")
            chart(fig, 320)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Reviews":
    st.markdown("<div class='main-wrapper'><div class='page-header'><div><div class='page-title'>Reviews & Ratings</div><div class='page-subtitle'>Customer satisfaction and product feedback</div></div><div class='page-badge'>★ Feedback</div></div></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='padding:0 32px'>", unsafe_allow_html=True)
        rkpi = q("SELECT COUNT(*) AS total_reviews, ROUND(AVG(rating)::numeric,2) AS avg_rating, SUM(CASE WHEN rating=5 THEN 1 ELSE 0 END) AS five_star, SUM(CASE WHEN rating<=2 THEN 1 ELSE 0 END) AS low_star FROM reviews")
        if not rkpi.empty:
            rk = rkpi.iloc[0]
            total_revs = int(rk['total_reviews'])
            pct5 = int(100 * int(rk['five_star']) / total_revs) if total_revs > 0 else 0
            rev_total_val = f"{total_revs:,}"
            rev_avg_val = f"{rk['avg_rating']} / 5"
            rev_5star_val = f"{int(rk['five_star']):,}"
            rev_pct_sub = f"{pct5}% of total"
            rev_low_val = f"{int(rk['low_star']):,}"
            st.markdown(f"<div class='kpi-row'>{kpi_card('Total Reviews', rev_total_val, 'All time', 'gold', '★')}{kpi_card('Average Rating', rev_avg_val, 'Overall score', 'teal', '◎')}{kpi_card('5-Star Reviews', rev_5star_val, rev_pct_sub, 'sky', '★', 'up')}{kpi_card('Low Ratings', rev_low_val, '1–2 star reviews', 'rose', '↓')}</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="medium")
        sec("RATING DISTRIBUTION")
        with col1:
            st.markdown("<div class='chart-card'><div class='chart-title'>Rating Breakdown</div>", unsafe_allow_html=True)
            rdist = q("SELECT rating, COUNT(*) AS cnt FROM reviews GROUP BY rating ORDER BY rating")
            if not rdist.empty:
                STAR_C = {1:"#FB7185", 2:"#F97316", 3:"#E8C547", 4:"#38BDF8", 5:"#2DD4BF"}
                fig = go.Figure(go.Bar(x=[str(r) + " ★" for r in rdist["rating"]], y=rdist["cnt"], marker=dict(color=[STAR_C[r] for r in rdist["rating"]], line_width=0), text=rdist["cnt"], textposition="outside", textfont=dict(size=12, color="#94A3B8"), hovertemplate="<b>%{x}</b><br>%{y} reviews<extra></extra>"))
                fig.update_layout(xaxis_title="", yaxis_title="", bargap=0.35, showlegend=False)
                chart(fig, 280)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='chart-card'><div class='chart-title'>Avg Rating by Category</div>", unsafe_allow_html=True)
            catrating = q("SELECT c.name AS category, ROUND(AVG(r.rating)::numeric,2) AS avg_rating FROM reviews r JOIN products pr ON r.product_id=pr.product_id JOIN categories c ON pr.category_id=c.category_id GROUP BY c.name ORDER BY avg_rating DESC")
            if not catrating.empty:
                fig = go.Figure(go.Bar(y=catrating["category"], x=catrating["avg_rating"], orientation="h", marker=dict(color=catrating["avg_rating"], colorscale=[[0,"#1A2332"],[0.5,"#E8C547"],[1,"#2DD4BF"]], showscale=False, line_width=0), text=catrating["avg_rating"], textposition="outside", textfont=dict(size=11, color="#94A3B8"), hovertemplate="<b>%{y}</b><br>%{x} stars<extra></extra>"))
                fig.update_layout(yaxis_autorange="reversed", xaxis_range=[0, 5.8], showlegend=False)
                chart(fig, 280)
            st.markdown("</div>", unsafe_allow_html=True)
        sec("TOP REVIEWED PRODUCTS")
        st.markdown("<div class='chart-card'><div class='chart-title'>Reviews vs Rating — Bubble Chart</div>", unsafe_allow_html=True)
        top_rev = q("SELECT pr.name AS product, COUNT(r.review_id) AS reviews, ROUND(AVG(r.rating)::numeric,2) AS avg_rating FROM reviews r JOIN products pr ON r.product_id=pr.product_id GROUP BY pr.name ORDER BY reviews DESC LIMIT 14")
        if not top_rev.empty:
            fig = px.scatter(top_rev, x="reviews", y="avg_rating", text="product", size="reviews", size_max=40, color="avg_rating", color_continuous_scale=[[0,"#FB7185"],[0.5,"#E8C547"],[1,"#2DD4BF"]], labels={"reviews": "Number of Reviews", "avg_rating": "Avg Rating"})
            fig.update_traces(textposition="top center", textfont=dict(size=10, color="#94A3B8"), marker=dict(line=dict(width=1.5, color=CHART_BG), opacity=0.9))
            fig.update_coloraxes(showscale=False)
            fig.update_layout(yaxis_range=[0, 5.8])
            chart(fig, 360)
        st.markdown("</div>", unsafe_allow_html=True)
        sec("RECENT REVIEWS")
        recent = q("SELECT cu.name AS customer, pr.name AS product, r.rating, r.comment, r.review_date FROM reviews r JOIN customers cu ON r.customer_id=cu.customer_id JOIN products pr ON r.product_id=pr.product_id ORDER BY r.review_date DESC LIMIT 15")
        if not recent.empty:
            st.dataframe(recent, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "SQL Explorer":
    st.markdown("<div class='main-wrapper'><div class='page-header'><div><div class='page-title'>SQL Explorer</div><div class='page-subtitle'>Run any query directly on your PostgreSQL database</div></div><div class='page-badge'>⌗ Query</div></div></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='padding:0 32px'>", unsafe_allow_html=True)
        SAMPLES = {
            "Monthly Revenue": "SELECT TO_CHAR(DATE_TRUNC('month', o.order_date), 'Mon YYYY') AS month, COUNT(DISTINCT o.order_id) AS total_orders, ROUND(SUM(p.amount)::numeric, 2) AS total_revenue FROM orders o JOIN payments p ON o.order_id = p.order_id WHERE o.order_status = 'delivered' GROUP BY DATE_TRUNC('month', o.order_date) ORDER BY DATE_TRUNC('month', o.order_date);",
            "Top 10 Customers": "SELECT cu.name, COUNT(o.order_id) AS orders, ROUND(SUM(p.amount)::numeric, 2) AS total_spent FROM customers cu JOIN orders o ON cu.customer_id = o.customer_id JOIN payments p ON o.order_id = p.order_id GROUP BY cu.name ORDER BY total_spent DESC LIMIT 10;",
            "Category Performance": "SELECT c.name AS category, COUNT(oi.order_item_id) AS units_sold, ROUND(SUM(oi.unit_price * oi.quantity)::numeric, 2) AS revenue FROM order_items oi JOIN products pr ON oi.product_id = pr.product_id JOIN categories c ON pr.category_id = c.category_id GROUP BY c.name ORDER BY revenue DESC;",
            "Stock Orders": "SELECT s.name AS seller, COUNT(so.lot_order_id) AS orders, SUM(so.lot_order_amount) AS total_units, so.lot_order_status FROM stock_orders so JOIN sellers s ON so.seller_id = s.seller_id GROUP BY s.name, so.lot_order_status ORDER BY total_units DESC;",
            "Product Reviews": "SELECT pr.name AS product, COUNT(r.review_id) AS reviews, ROUND(AVG(r.rating)::numeric, 2) AS avg_rating FROM reviews r JOIN products pr ON r.product_id = pr.product_id GROUP BY pr.name ORDER BY avg_rating DESC, reviews DESC;",
        }
        sec("QUICK QUERIES")
        chips_html = "".join([f"<span class='sql-chip'>{k}</span>" for k in SAMPLES])
        st.markdown(chips_html, unsafe_allow_html=True)
        selected = st.selectbox("Load a sample query", ["— write your own —"] + list(SAMPLES.keys()), label_visibility="collapsed")
        default_sql = SAMPLES.get(selected, "SELECT * FROM categories LIMIT 10;")
        sec("QUERY EDITOR")
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        sql_input = st.text_area("SQL", value=default_sql, height=160, label_visibility="collapsed", placeholder="Write your SQL query here...")
        st.markdown("</div>", unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns([1, 2, 3])
        with col_a: run_btn = st.button("▶ Run Query", use_container_width=True)
        with col_b: chart_type = st.selectbox("Chart type", ["Table only", "Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot"], label_visibility="collapsed")
        if run_btn and sql_input.strip():
            try:
                result = q(sql_input)
                if not result.empty:
                    st.success(f"✔  {len(result):,} rows returned")
                    sec("RESULTS")
                    st.dataframe(result, use_container_width=True, hide_index=True)
                    num_cols = result.select_dtypes("number").columns.tolist()
                    str_cols = result.select_dtypes("object").columns.tolist()
                    if chart_type != "Table only" and num_cols and str_cols:
                        x_col, y_col = str_cols[0], num_cols[0]
                        sec("VISUALISATION")
                        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
                        if chart_type == "Bar Chart": fig = go.Figure(go.Bar(x=result[x_col], y=result[y_col], marker=dict(color=PALETTE[0], line_width=0)))
                        elif chart_type == "Line Chart": fig = go.Figure(go.Scatter(x=result[x_col], y=result[y_col], mode="lines+markers", line=dict(color=PALETTE[1], width=2.5), marker=dict(size=7, color=PALETTE[1])))
                        elif chart_type == "Pie Chart": fig = go.Figure(go.Pie(labels=result[x_col], values=result[y_col], hole=0.5, marker=dict(colors=PALETTE, line=dict(color=CHART_BG, width=2))))
                        elif chart_type == "Scatter Plot" and len(num_cols) >= 2: fig = px.scatter(result, x=num_cols[0], y=num_cols[1], hover_name=x_col, color_discrete_sequence=[PALETTE[0]])
                        else: fig = go.Figure(go.Bar(x=result[x_col], y=result[y_col], marker=dict(color=PALETTE[0], line_width=0)))
                        chart(fig, 360)
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("Query returned no results.")
            except Exception as e: st.error(f"Query error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
