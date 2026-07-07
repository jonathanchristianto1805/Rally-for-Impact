import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
from pathlib import Path

# Configure Streamlit
st.set_page_config(
    page_title="Rally for Impact - Prediction Market",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS untuk styling
st.markdown("""
    <style>
    /* General styling */
    :root {
        --primary: #1a472a;
        --secondary: #d4a574;
        --accent: #e8795c;
        --light: #f5f5f5;
        --dark: #2d2d2d;
    }
    
    /* Main container */
    .main {
        background-color: #ffffff;
    }
    
    /* Header */
    .header-section {
        background: linear-gradient(135deg, #1a472a 0%, #2d5a3d 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .header-section h1 {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .header-section .tagline {
        font-size: 1.1rem;
        color: #d4a574;
        font-weight: 500;
    }
    
    /* Match cards */
    .match-card {
        background: linear-gradient(135deg, #f9f9f9 0%, #f0f0f0 100%);
        border-left: 5px solid #e8795c;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .match-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1a472a;
        margin-bottom: 1rem;
    }
    
    .team-option {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .team-option:hover {
        border-color: #e8795c;
        box-shadow: 0 4px 12px rgba(232, 121, 92, 0.15);
    }
    
    .team-option.selected {
        border-color: #d4a574;
        background: #fffaf5;
    }
    
    .team-name {
        font-size: 1.1rem;
        font-weight: bold;
        color: #1a472a;
    }
    
    .team-odds {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* Input section */
    .donation-input {
        background: #f9f9f9;
        border: 2px solid #d4a574;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    .donation-label {
        font-size: 1rem;
        font-weight: 600;
        color: #1a472a;
        margin-bottom: 0.5rem;
    }
    
    /* Statistics */
    .stats-box {
        background: linear-gradient(135deg, #1a472a 0%, #2d5a3d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .stats-value {
        font-size: 2rem;
        font-weight: bold;
        color: #d4a574;
    }
    
    .stats-label {
        font-size: 0.9rem;
        color: #b0b0b0;
        margin-top: 0.5rem;
    }
    
    /* Button styling */
    .submit-btn {
        background: linear-gradient(135deg, #e8795c 0%, #d97547 100%);
        color: white;
        padding: 1rem 2rem;
        border: none;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .submit-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(232, 121, 92, 0.3);
    }
    
    /* Summary section */
    .summary-box {
        background: #f0fdf4;
        border: 2px solid #86efac;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    .summary-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #15803d;
        margin-bottom: 1rem;
    }
    
    .summary-item {
        padding: 0.5rem 0;
        color: #166534;
    }
    
    /* Donation info */
    .donation-info {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 5px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 2rem;
    }
    
    .donation-info-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #92400e;
        margin-bottom: 0.5rem;
    }
    
    .donation-info-text {
        color: #b45309;
        line-height: 1.6;
    }
    
    .donation-account {
        background: white;
        padding: 1rem;
        border-radius: 6px;
        margin-top: 1rem;
        font-family: monospace;
        text-align: center;
        font-weight: bold;
        color: #1a472a;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'predictions' not in st.session_state:
    st.session_state.predictions = []

if 'total_pot' not in st.session_state:
    st.session_state.total_pot = 0

# Data structure
MATCHES = [
    {
        'id': 1,
        'name': 'Pertandingan 1: Exhibition Match',
        'teams': [
            {'name': 'Tim A', 'probability': 0.48},
            {'name': 'Tim B', 'probability': 0.52}
        ]
    },
    {
        'id': 2,
        'name': 'Pertandingan 2: Exhibition Match',
        'teams': [
            {'name': 'Tim C', 'probability': 0.45},
            {'name': 'Tim D', 'probability': 0.55}
        ]
    }
]

def calculate_odds(probability):
    """Calculate decimal odds from probability"""
    return round(1 / probability, 2)

def format_currency(amount):
    """Format amount as Indonesian Rupiah"""
    return f"Rp {amount:,.0f}"

# Header
st.markdown("""
    <div class="header-section">
        <h1>🎯 Rally for Impact</h1>
        <div class="tagline">Prediction Market untuk Amal</div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
### Cara Bermain
1. Pilih tim yang menurut Anda akan menang di setiap pertandingan
2. Masukkan nominal donasi Anda (minimal Rp 10.000)
3. Semua dana yang terkumpul akan didonasikan untuk amal
4. Jika prediksi Anda benar, hadiah akan dibagikan kepada para pemenang
""")

# Main content
st.markdown("---")

# Track selections
match1_selection = None
match2_selection = None
donation_amount = 0

col1, col2 = st.columns(2)

# Match 1
with col1:
    st.markdown('<div class="match-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="match-title">{MATCHES[0]["name"]}</div>', unsafe_allow_html=True)
    
    match1_choice = st.radio(
        "Pilih pemenang:",
        options=[f"{team['name']} (Odds: {calculate_odds(team['probability'])}x)" 
                for team in MATCHES[0]['teams']],
        key="match1",
        label_visibility="collapsed"
    )
    match1_selection = MATCHES[0]['teams'][0 if 'Tim A' in match1_choice else 1]
    st.markdown('</div>', unsafe_allow_html=True)

# Match 2
with col2:
    st.markdown('<div class="match-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="match-title">{MATCHES[1]["name"]}</div>', unsafe_allow_html=True)
    
    match2_choice = st.radio(
        "Pilih pemenang:",
        options=[f"{team['name']} (Odds: {calculate_odds(team['probability'])}x)" 
                for team in MATCHES[1]['teams']],
        key="match2",
        label_visibility="collapsed"
    )
    match2_selection = MATCHES[1]['teams'][0 if 'Tim C' in match2_choice else 1]
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Donation input
st.markdown('<div class="donation-input">', unsafe_allow_html=True)
st.markdown('<div class="donation-label">💰 Nominal Donasi (dalam Rupiah)</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    donation_amount = st.number_input(
        "Masukkan nominal donasi Anda",
        min_value=10000,
        step=10000,
        value=100000,
        label_visibility="collapsed"
    )

with col2:
    st.metric("Total", format_currency(donation_amount))

st.markdown('</div>', unsafe_allow_html=True)

# Calculate potential winnings
combined_odds = calculate_odds(match1_selection['probability']) * calculate_odds(match2_selection['probability'])
potential_winnings = donation_amount * combined_odds

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="stats-box">
        <div class="stats-value">{combined_odds:.2f}x</div>
        <div class="stats-label">Combined Odds</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stats-box">
        <div class="stats-value">{format_currency(donation_amount)}</div>
        <div class="stats-label">Nominal Donasi</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stats-box">
        <div class="stats-value">{format_currency(int(potential_winnings))}</div>
        <div class="stats-label">Potensi Hadiah (jika menang)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Summary before submission
st.markdown('<div class="summary-box">', unsafe_allow_html=True)
st.markdown('<div class="summary-title">📋 Ringkasan Prediksi Anda</div>', unsafe_allow_html=True)

summary_html = f"""
<div class="summary-item">
    <strong>Pertandingan 1:</strong> {match1_selection['name']} (Odds: {calculate_odds(match1_selection['probability'])}x)
</div>
<div class="summary-item">
    <strong>Pertandingan 2:</strong> {match2_selection['name']} (Odds: {calculate_odds(match2_selection['probability'])}x)
</div>
<div class="summary-item">
    <strong>Nominal Donasi:</strong> {format_currency(donation_amount)}
</div>
<div class="summary-item">
    <strong>Potensi Hadiah:</strong> {format_currency(int(potential_winnings))}
</div>
"""
st.markdown(summary_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Submit button
if st.button("✅ Konfirmasi Prediksi & Donasi", use_container_width=True, key="submit_btn"):
    prediction = {
        'timestamp': datetime.now().isoformat(),
        'match1': match1_selection['name'],
        'match2': match2_selection['name'],
        'amount': donation_amount,
        'potential_winnings': int(potential_winnings),
        'odds': combined_odds
    }
    st.session_state.predictions.append(prediction)
    st.session_state.total_pot += donation_amount
    
    st.success(f"""
    ✅ **Prediksi Anda Berhasil Disimpan!**
    
    Terima kasih telah berpartisipasi dalam Rally for Impact.
    
    Nominal donasi Anda: **{format_currency(donation_amount)}**
    
    Total dana terkumpul: **{format_currency(int(st.session_state.total_pot))}**
    
    Silakan lanjutkan ke bagian berikutnya untuk menyelesaikan transaksi.
    """)

st.markdown("---")

# Donation instructions
st.markdown("""
<div class="donation-info">
    <div class="donation-info-title">💳 Cara Transfer Donasi Anda</div>
    <div class="donation-info-text">
        Setelah mengkonfirmasi prediksi Anda, silakan transfer nominal donasi ke rekening berikut:
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    **Bank BCA**
    """)
    st.markdown("""
    <div class="donation-account">
    1234567890<br>
    (Rally for Impact)
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    **Bank Mandiri**
    """)
    st.markdown("""
    <div class="donation-account">
    0987654321<br>
    (Rally for Impact)
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    **E-Wallet (GCash/Dana)**
    """)
    st.markdown("""
    <div class="donation-account">
    +62 812-3456-7890<br>
    (Rally for Impact)
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
**Catatan:** 
- Pastikan nominal transfer sesuai dengan nominal yang Anda inputkan di atas
- Konfirmasi transfer melalui WhatsApp ke nomor yang tersedia di halaman ini
- Anda akan dihubungi kembali untuk verifikasi
""")

st.markdown("---")

# Live statistics
st.markdown("### 📊 Statistik Live")

if st.session_state.predictions:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Prediksi", len(st.session_state.predictions))
    
    with col2:
        avg_donation = st.session_state.total_pot / len(st.session_state.predictions)
        st.metric("Rata-rata Donasi", format_currency(int(avg_donation)))
    
    with col3:
        st.metric("Total Dana Terkumpul", format_currency(int(st.session_state.total_pot)))
    
    with col4:
        total_potential = sum(p['potential_winnings'] for p in st.session_state.predictions)
        st.metric("Total Hadiah Potensial", format_currency(total_potential))
    
    # Chart
    fig = go.Figure(data=[
        go.Pie(
            labels=['Tim A', 'Tim B', 'Tim C', 'Tim D'],
            values=[
                len([p for p in st.session_state.predictions if 'Tim A' in p['match1']]),
                len([p for p in st.session_state.predictions if 'Tim B' in p['match1']]),
                len([p for p in st.session_state.predictions if 'Tim C' in p['match2']]),
                len([p for p in st.session_state.predictions if 'Tim D' in p['match2']])
            ],
            marker=dict(colors=['#1a472a', '#d4a574', '#e8795c', '#2d5a3d'])
        )
    ])
    fig.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Belum ada prediksi. Mulai dengan membuat prediksi Anda di atas!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem;'>
    <p><strong>Rally for Impact</strong> - Prediction Market untuk Amal</p>
    <p style='font-size: 0.9rem;'>Semua dana yang terkumpul akan didonasikan untuk acara amal.</p>
</div>
""", unsafe_allow_html=True)
