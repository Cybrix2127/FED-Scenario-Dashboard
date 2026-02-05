import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from Calculation import compute_monthly, fomc_dates, month_options

st.set_page_config(layout="wide")

st.title("Fed Scenario Calculator")

# ------------------------
# INPUT SECTION
# ------------------------

col1, col2 = st.columns(2)

with col1:
    effr_spot = st.number_input("EFFR Spot (%)", value=3.75, format="%.4f")
    sofr_spot = st.number_input("SOFR Spot (%)", value=3.73, format="%.4f")

with col2:
    m_premium = st.slider("Month End Premium (bps)", 0.0, 50.0, 2.0, 0.5)
    q_premium = st.slider("Quarter End Premium (bps)", 0.0, 100.0, 5.0, 0.5)
    y_premium = st.slider("Year End Premium (bps)", 0.0, 200.0, 15.0, 0.5)

st.markdown("### FOMC Meeting Adjustments (bps)")

slider_cols = st.columns(4)
sliders_dict = {}

for i, d in enumerate(fomc_dates):
    with slider_cols[i % 4]:
        sliders_dict[d] = st.slider(d, -50, 50, 0, 25)

month_a = st.selectbox("Month A", month_options, index=2)
month_b = st.selectbox("Month B", month_options, index=5)
contract_type = st.selectbox("Contract", ["ZQ (Fed Funds)", "SR1 (SOFR)"])

# ------------------------
# CALCULATION
# ------------------------

effr_daily, sofr_daily, df = compute_monthly(
    effr_spot,
    sofr_spot,
    sliders_dict,
    m_premium,
    q_premium,
    y_premium
)

# ------------------------
# TABS
# ------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "Rates & Hike Path",
    "Spread Change",
    "Compare Outrights",
    "Compare Basis"
])

# ------------------------
# TAB 1
# ------------------------

with tab1:
    total_change = sum(sliders_dict.values())
    st.write(f"Total Scenario Policy Change: {total_change:+.2f} bps")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=effr_daily.index,
        y=effr_daily,
        name="EFFR",
        line=dict(width=2)
    ))

    fig.add_trace(go.Scatter(
        x=sofr_daily.index,
        y=sofr_daily,
        name="SOFR",
        line=dict(width=2)
    ))

    for d in fomc_dates:
        fig.add_vline(x=d, line_width=1, line_dash="dot")

    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------
# TAB 2
# ------------------------

with tab2:
    col = 'EFFR_Avg' if "ZQ" in contract_type else 'SOFR_Avg'
    diff_bps = (df.loc[month_b, col] - df.loc[month_a, col]) * 100

    st.write(f"Spread Change: {diff_bps:+.4f} bps")

    fig = go.Figure()
    fig.add_bar(
        x=[month_a, month_b],
        y=[df.loc[month_a, col], df.loc[month_b, col]]
    )

    fig.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------
# TAB 3
# ------------------------

with tab3:
    col = 'ZQ_Outright' if "ZQ" in contract_type else 'SR1_Outright'
    p1, p2 = df.loc[month_a, col], df.loc[month_b, col]

    st.write(f"{month_a}: {p1:.4f}")
    st.write(f"{month_b}: {p2:.4f}")
    st.write(f"Price Delta: {p2-p1:+.4f}")

    fig = go.Figure()
    fig.add_bar(x=[month_a, month_b], y=[p1, p2])

    fig.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------
# TAB 4
# ------------------------

with tab4:
    df['Basis'] = (df['ZQ_Outright'] - df['SR1_Outright']) * 100

    basis_a = df.loc[month_a, 'Basis']
    basis_b = df.loc[month_b, 'Basis']

    st.write(f"Basis
