import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
import time
import os

st.set_page_config(
    page_title="CryptoLens · Real-time Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Root variables ── */
:root {
    --bg-primary:   #F7F9FC;
    --bg-card:      #FFFFFF;
    --bg-subtle:    #EEF2F8;
    --accent:       #1A56DB;
    --accent-light: #EBF0FF;
    --accent-teal:  #0891B2;
    --accent-green: #059669;
    --accent-red:   #DC2626;
    --text-primary: #0F172A;
    --text-secondary: #64748B;
    --border:       #E2E8F0;
    --shadow-sm:    0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04);
    --shadow-md:    0 4px 16px rgba(15,23,42,0.08), 0 2px 6px rgba(15,23,42,0.05);
    --radius:       12px;
}

/* ── Base resets ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1400px;
}

/* ── Page header ── */
.page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 1.75rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.page-header-left {
    display: flex;
    align-items: center;
    gap: 14px;
}
.logo-badge {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #1A56DB 0%, #0891B2 100%);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
}
.page-title {
    font-size: 1.35rem;
    font-weight: 600;
    letter-spacing: -0.3px;
    color: var(--text-primary);
    margin: 0;
}
.page-subtitle {
    font-size: 0.78rem;
    color: var(--text-secondary);
    margin: 0;
    font-weight: 400;
}
.live-badge {
    display: flex; align-items: center; gap: 6px;
    background: #ECFDF5;
    color: #047857;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 20px;
    border: 1px solid #A7F3D0;
}
.live-dot {
    width: 7px; height: 7px;
    background: #10B981;
    border-radius: 50%;
    animation: pulse 1.8s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── Metric cards ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s;
}
.metric-card:hover { box-shadow: var(--shadow-md); }
.metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 8px;
}
.metric-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.65rem;
    font-weight: 500;
    color: var(--text-primary);
    letter-spacing: -0.5px;
    line-height: 1;
    margin-bottom: 6px;
}
.metric-delta-pos {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--accent-green);
}
.metric-delta-neg {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--accent-red);
}
.metric-delta-neutral {
    font-size: 0.78rem;
    color: var(--text-secondary);
}

/* ── Section headers ── */
.section-header {
    display: flex; align-items: center; gap: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    margin-top: 1.75rem;
}
.section-tag {
    background: var(--accent-light);
    color: var(--accent);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
}

/* ── Info strip ── */
.info-strip {
    background: var(--accent-light);
    border: 1px solid #C7D7F8;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 0.78rem;
    color: var(--accent);
    display: flex; align-items: center; gap: 8px;
}

/* ── Chart container ── */
.chart-wrapper {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1.25rem;
}

/* ── Divider ── */
hr { border: none; border-top: 1px solid var(--border) !important; margin: 1.75rem 0 !important; }

/* ── Dataframe ── */
.stDataFrame { border-radius: 8px; overflow: hidden; }
div[data-testid="stDataFrameResizable"] { border: 1px solid var(--border) !important; border-radius: 8px; }

/* ── Warning / error ── */
.stAlert { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)


# 2. DB FUNCTIONS  

def get_db_connection():
    db_host = os.environ.get('DB_HOST', 'postgres')
    return psycopg2.connect(
        host=db_host,
        database="crypto_dw",
        user="loc_admin",
        password="password123",
        port="5432"
    )

def get_silver_data():
    try:
        conn = get_db_connection()
        query = "SELECT symbol, price, trade_time FROM crypto_prices_cleaned ORDER BY trade_time DESC LIMIT 100"
        df = pd.read_sql(query, conn)
        conn.close()
        if not df.empty:
            df['trade_time'] = pd.to_datetime(df['trade_time']) + pd.Timedelta(hours=7)
        return df
    except Exception as e:
        st.error(f"Silver Layer Error: {e}")
        return pd.DataFrame()

def get_gold_data():
    try:
        conn = get_db_connection()
        query = "SELECT * FROM crypto_hourly_stats ORDER BY hour_timestamp DESC LIMIT 10"
        df = pd.read_sql(query, conn)
        conn.close()
        if not df.empty:
            df['hour_timestamp'] = pd.to_datetime(df['hour_timestamp']) + pd.Timedelta(hours=7)
        return df
    except Exception as e:
        st.error(f"Gold Layer Error: {e}")
        return pd.DataFrame()

# 3. CHART THEME (light professional)
CHART_LAYOUT = dict(
    font=dict(family="DM Sans, sans-serif", size=12, color="#0F172A"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=36, b=10),
    title_font=dict(size=13, color="#0F172A", family="DM Sans, sans-serif"),
    title_x=0,
    xaxis=dict(
        gridcolor="#E2E8F0", gridwidth=1,
        linecolor="#E2E8F0", tickfont=dict(size=11, color="#64748B"),
        showgrid=True, zeroline=False,
    ),
    yaxis=dict(
        gridcolor="#E2E8F0", gridwidth=1,
        linecolor="#E2E8F0", tickfont=dict(size=11, color="#64748B"),
        showgrid=True, zeroline=False,
    ),
    legend=dict(
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#E2E8F0", borderwidth=1,
        font=dict(size=11),
    ),
    hoverlabel=dict(
        bgcolor="white", bordercolor="#E2E8F0",
        font=dict(size=12, color="#0F172A"),
    ),
)

# 4. MAIN LOOP
placeholder = st.empty()

while True:
    with placeholder.container():

        # ── Page Header ──
        st.markdown("""
        <div class="page-header">
            <div class="page-header-left">
                <div class="logo-badge">📊</div>
                <div>
                    <p class="page-title">CryptoLens Analytics</p>
                    <p class="page-subtitle">Real-time Medallion Architecture · Kafka → Bronze → Silver → Gold</p>
                </div>
            </div>
            <div class="live-badge">
                <div class="live-dot"></div>
                Live · GMT+7
            </div>
        </div>
        """, unsafe_allow_html=True)

        df_silver = get_silver_data()
        df_gold   = get_gold_data()

        if not df_silver.empty:

            # ── KPI Metrics ──
            current_price = df_silver['price'].iloc[0]
            prev_price    = df_silver['price'].iloc[1] if len(df_silver) > 1 else current_price
            delta         = current_price - prev_price
            delta_pct     = (delta / prev_price * 100) if prev_price else 0

            if delta > 0:
                delta_html = f'<div class="metric-delta-pos">▲ ${delta:,.2f} &nbsp;({delta_pct:+.3f}%)</div>'
            elif delta < 0:
                delta_html = f'<div class="metric-delta-neg">▼ ${abs(delta):,.2f} &nbsp;({delta_pct:.3f}%)</div>'
            else:
                delta_html = '<div class="metric-delta-neutral">— No change</div>'

            last_update = df_silver['trade_time'].iloc[0].strftime("%H:%M:%S")
            record_count = len(df_silver)

            col1, col2, col3, col4 = st.columns([1.4, 1, 1, 1.6])

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Bitcoin · BTC/USDT</div>
                    <div class="metric-value">${current_price:,.2f}</div>
                    {delta_html}
                </div>""", unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Last Updated</div>
                    <div class="metric-value" style="font-size:1.35rem">{last_update}</div>
                    <div class="metric-delta-neutral">Vietnam Time (GMT+7)</div>
                </div>""", unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Records Loaded</div>
                    <div class="metric-value" style="font-size:1.35rem">{record_count}</div>
                    <div class="metric-delta-neutral">Silver layer · latest 100</div>
                </div>""", unsafe_allow_html=True)

            with col4:
                st.markdown("""
                <div class="info-strip">
                    ⚡ &nbsp;<strong>Pipeline:</strong> &nbsp;Kafka &nbsp;→&nbsp; Bronze (raw) &nbsp;→&nbsp; ELT &nbsp;→&nbsp; Silver (cleaned) &nbsp;→&nbsp; Gold (aggregated) &nbsp;→&nbsp; Streamlit
                </div>""", unsafe_allow_html=True)

            # ── Silver Chart ──
            st.markdown("""
            <div class="section-header">
                📈 &nbsp;Price Movement &nbsp;<span class="section-tag">Silver Layer</span>
            </div>""", unsafe_allow_html=True)

            df_sorted = df_silver.sort_values('trade_time')
            df_sorted['SMA_10'] = df_sorted['price'].rolling(window=10).mean()

            fig = go.Figure()

            # Fill area under price
            fig.add_trace(go.Scatter(
                x=df_sorted['trade_time'], y=df_sorted['price'],
                fill='tozeroy',
                fillcolor='rgba(26, 86, 219, 0.07)',
                line=dict(color='#1A56DB', width=2),
                name='BTC Price',
                hovertemplate='<b>%{x|%H:%M:%S}</b><br>$%{y:,.2f}<extra></extra>',
            ))

            # SMA line
            fig.add_trace(go.Scatter(
                x=df_sorted['trade_time'], y=df_sorted['SMA_10'],
                line=dict(color='#F59E0B', width=2, dash='dot'),
                name='SMA(10)',
                hovertemplate='SMA10: $%{y:,.2f}<extra></extra>',
            ))

            fig.update_layout(
                title="100 Most Recent Trades + SMA(10)  ·  GMT+7",
                **CHART_LAYOUT,
                height=340,
                xaxis_title="",
                yaxis_title="",
            )

            st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, key=f"silver_{time.time()}")
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Gold Layer ──
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("""
            <div class="section-header">
                🏆 &nbsp;Hourly Aggregations &nbsp;<span class="section-tag">Gold Layer</span>
            </div>""", unsafe_allow_html=True)

            if not df_gold.empty:
                col_g1, col_g2 = st.columns([2, 1])

                with col_g1:
                    fig_gold = go.Figure()

                    fig_gold.add_trace(go.Bar(
                        x=df_gold['hour_timestamp'], y=df_gold['max_price'],
                        name='Max Price',
                        marker_color='#1A56DB',
                        marker_line_width=0,
                        hovertemplate='Max: $%{y:,.2f}<extra></extra>',
                    ))
                    fig_gold.add_trace(go.Bar(
                        x=df_gold['hour_timestamp'], y=df_gold['min_price'],
                        name='Min Price',
                        marker_color='#BAD7F7',
                        marker_line_width=0,
                        hovertemplate='Min: $%{y:,.2f}<extra></extra>',
                    ))

                    fig_gold.update_layout(
                        title="Max / Min Price Range per Hour  ·  GMT+7",
                        barmode='group',
                        **CHART_LAYOUT,
                        height=300,
                        bargap=0.3,
                        bargroupgap=0.05,
                    )

                    st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
                    st.plotly_chart(fig_gold, use_container_width=True, key=f"gold_{time.time()}")
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_g2:
                    st.markdown("""
                    <div style="font-size:0.72rem; font-weight:700; letter-spacing:0.8px;
                                text-transform:uppercase; color:#64748B; margin-bottom:10px;">
                        Serving Layer · Summary Table
                    </div>""", unsafe_allow_html=True)

                    display_df = df_gold[['hour_timestamp', 'avg_price', 'total_records']].copy()
                    display_df.columns = ['Hour (GMT+7)', 'Avg Price', 'Records']
                    display_df['Avg Price'] = display_df['Avg Price'].apply(lambda x: f"${x:,.2f}")
                    st.dataframe(display_df, hide_index=True, use_container_width=True)

        else:
            st.warning("⏳ Awaiting data... Please verify the ELT job is running.")

    time.sleep(2)