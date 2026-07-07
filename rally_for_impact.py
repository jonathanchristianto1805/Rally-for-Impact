import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
import time
import os

# -------------------------
# File paths
# -------------------------
BETS_FILE = "bets.csv"
ODDS_FILE = "odds_history.csv"

# -------------------------
# Load/save data from file if available
# -------------------------
def load_bets():
    if os.path.exists(BETS_FILE):
        return pd.read_csv(BETS_FILE)
    else:
        return pd.DataFrame(columns=['Name', 'Choice', 'Bet'])

def save_bets(df):
    df.to_csv(BETS_FILE, index=False)

def load_odds():
    if os.path.exists(ODDS_FILE):
        df = pd.read_csv(ODDS_FILE)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    else:
        return pd.DataFrame(columns=['Timestamp', 'Team 1', 'Team 2'])

def save_odds(df):
    df.to_csv(ODDS_FILE, index=False)

# -------------------------
# Session Initialization
# -------------------------
if 'bets' not in st.session_state:
    st.session_state.bets = load_bets()

if 'which_team' not in st.session_state:
    st.session_state.which_team = None

if 'odds_history' not in st.session_state:
    st.session_state.odds_history = load_odds()

# -------------------------
# Page Config & Styling
# -------------------------
st.set_page_config(page_title="Rally for Impact Market 🎉", layout="centered")

st.markdown("""
<style>
.stApp, .block-container {
    background-color: #fff9c4 !important;
    color: #212121 !important;
}
.stMarkdown h1, h2, h3, p, ul, ol, strong, em {
    color: #212121 !important;
}
input, textarea, select {
    background-color: #ffffff !important;
    color: #212121 !important;
}
.stButton > button {
    background-color: #212121 !important;
    color: #fff9c4 !important;
}
.stDataFrame, .stTable {
    color: #212121 !important;
    background-color: #fffde7 !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Handle Pop-out View Mode
# -------------------------
query_params = dict(st.query_params)
popout_mode = query_params.get("view")
if isinstance(popout_mode, list):
    popout_mode = popout_mode[0]

# -------------------------
# Optional: Logo and Title
# -------------------------
if not popout_mode:
    # st.image("Salinan dari KV Rally of Impact.png", width=1000)  # Comment jika image tidak ada
    st.markdown(
        """
        <h1 style='text-align: center;'>
            🎉 Rally for Impact Market (Rupiah) - Real Money, % for Charity
        </h1>
        <p style='text-align: center; font-size: 18px; color: #212121;'>
            Everyone places a bet on either <strong>'Team 1'</strong> or <strong>'Team 2'</strong>.<br>
            Winners share the loser pool money proportionally. The multiplier is calculated at the end of the event.
            <br>
            <em>Note:</em> 20% of each winner's profit will be donated to a chosen non-profit.
            <br>
            <strong>📌 Please transfer your bet amount to: <u>6500887786 a/n Joseph Ian Tanuri</u></strong><br>
            <strong><em>"Untuk Kalangan Sendiri"</em></strong>
        </p>
        """,
        unsafe_allow_html=True
    )

# -------------------------
# Place Your Bet Section
# -------------------------
if not popout_mode:
    with st.expander("📌 Place Your Bet"):
        with st.form("bet_form"):
            name = st.text_input("Your Name")
            choice = st.selectbox("Your Prediction", ["Team 1", "Team 2"])
            bet = st.number_input("Bet Amount (Rupiah)", min_value=10000, step=10000)
            submitted = st.form_submit_button("Place Bet")
            if submitted and name and bet > 0:
                new_bet = pd.DataFrame([[name, choice, bet]], columns=['Name', 'Choice', 'Bet'])
                st.session_state.bets = pd.concat([st.session_state.bets, new_bet], ignore_index=True)
                save_bets(st.session_state.bets)
                st.success(f"✅ Bet placed: {name} - {choice} - Rp {bet:,.0f}")
                st.rerun()

    # -------------------------
    # Show Bets + Remove Option
    # -------------------------
    st.header("📝 Current Bets")

    if not st.session_state.bets.empty:
        bets_display = st.session_state.bets.copy()
        bets_display['Bet'] = bets_display['Bet'].apply(lambda x: f"Rp {x:,.0f}")
        st.dataframe(bets_display, use_container_width=True)

        with st.expander("🗑️ Remove a Bet"):
            bet_index = st.number_input(
                "Row index to remove (starts at 0)",
                min_value=0,
                max_value=len(st.session_state.bets) - 1,
                step=1
            )
            if st.button("Remove Selected Bet"):
                st.session_state.bets = st.session_state.bets.drop(index=bet_index).reset_index(drop=True)
                save_bets(st.session_state.bets)
                st.rerun()
    else:
        st.info("No bets placed yet.")

# -------------------------
# Recalculate Totals & Odds (FIXED)
# -------------------------
total_team_1 = st.session_state.bets[st.session_state.bets['Choice'] == 'Team 1']['Bet'].sum()
total_team_2 = st.session_state.bets[st.session_state.bets['Choice'] == 'Team 2']['Bet'].sum()
total_pool = total_team_1 + total_team_2

# FIX: Konsisten pakai team_1_odds dan team_2_odds
team_1_odds = total_team_1 / total_pool if total_pool > 0 else 0
team_2_odds = total_team_2 / total_pool if total_pool > 0 else 0

# -------------------------
# Save Odds History (FIXED)
# -------------------------
if total_pool > 0:
    # Cek apakah odds berubah atau history kosong
    if st.session_state.odds_history.empty or (
        team_1_odds != st.session_state.odds_history.iloc[-1]['Team 1'] or
        team_2_odds != st.session_state.odds_history.iloc[-1]['Team 2']
    ):
        new_odds = pd.DataFrame([{
            'Timestamp': datetime.now(),
            'Team 1': team_1_odds,
            'Team 2': team_2_odds
        }])
        st.session_state.odds_history = pd.concat([
            st.session_state.odds_history,
            new_odds
        ], ignore_index=True)
        save_odds(st.session_state.odds_history)

# -------------------------
# Pop-out Views
# -------------------------
if popout_mode == "pie":
    st.markdown("""<meta http-equiv="refresh" content="20">""", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 36px;'>Place your bet: Team 1 or Team 2</h1>", unsafe_allow_html=True)
    
    try:
        bets = pd.read_csv(BETS_FILE)
        # Recalculate odds
        total_team_1 = bets[bets['Choice'] == 'Team 1']['Bet'].sum()
        total_team_2 = bets[bets['Choice'] == 'Team 2']['Bet'].sum()
        total_pool = total_team_1 + total_team_2
        team_1_odds = total_team_1 / total_pool if total_pool > 0 else 0
        team_2_odds = total_team_2 / total_pool if total_pool > 0 else 0

        st.markdown("## 📊 Live Market")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Team 1 Odds", f"{team_1_odds:.2%}")
        with col2:
            st.metric("Team 2 Odds", f"{team_2_odds:.2%}")

        st.markdown(f"**Total Pool:** Rp {total_pool:,.0f}")

        # Pie Chart
        if total_pool > 0:
            fig = px.pie(
                names=['Team 1', 'Team 2'],
                values=[total_team_1, total_team_2],
                color_discrete_sequence=['#1f77b4', '#ff69b4'],
                title='Current Bet Distribution'
            )
            fig.update_traces(textinfo='percent+label', pull=[0.05, 0.05])
            fig.update_layout(
                paper_bgcolor='#fff9c4',
                plot_bgcolor='#fff9c4',
                font_color='#212121'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Not enough data to render pie chart. Please place some bets.")
    except FileNotFoundError:
        st.warning("⚠️ No bets file found yet.")
    
    st.stop()

elif popout_mode == "line":
    st.markdown("<h1 style='text-align: center; font-size: 36px;'>Market Odds Over Time</h1>", unsafe_allow_html=True)
    
    try:
        odds = load_odds()
        if not odds.empty:
            fig = px.line(
                odds,
                x='Timestamp',
                y=['Team 1', 'Team 2'],
                markers=True,
                title='Live Odds Over Time',
                color_discrete_map={'Team 1': '#1f77b4', 'Team 2': '#ff69b4'}
            )
            fig.update_layout(
                paper_bgcolor='#fff9c4',
                plot_bgcolor='#fff9c4',
                font_color='#212121'
            )
            st.plotly_chart(fig, use_container_width=True)
            time.sleep(10)
            st.rerun()
        else:
            st.warning("⚠️ No odds history yet. Please place a bet.")
    except Exception as e:
        st.error(f"Error loading odds: {e}")
    
    st.stop()

# -------------------------
# MAIN DASHBOARD: Live Market + Admin
# -------------------------
if not popout_mode:
    st.header("📊 Live Market")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💙 Team 1 Odds", f"{team_1_odds:.2%}")
    with col2:
        st.metric("💖 Team 2 Odds", f"{team_2_odds:.2%}")

    st.write(f"**Total Pool:** Rp {total_pool:,.0f}")

    # Pie Chart
    if total_pool > 0:
        pie_fig = px.pie(
            names=['Team 1', 'Team 2'],
            values=[total_team_1, total_team_2],
            color_discrete_map={'Team 1': '#1f77b4', 'Team 2': '#ff69b4'},
            hole=0.3,
            title="Current Bet Distribution"
        )
        pie_fig.update_layout(paper_bgcolor='#fff9c4')
        st.plotly_chart(pie_fig, use_container_width=True)
    else:
        st.info("No bets placed yet.")

    # Line Chart
    if not st.session_state.odds_history.empty:
        line_fig = px.line(
            st.session_state.odds_history,
            x='Timestamp',
            y=['Team 1', 'Team 2'],
            markers=True,
            title='Market Probability History',
            color_discrete_map={'Team 1': '#1f77b4', 'Team 2': '#ff69b4'}
        )
        line_fig.update_layout(paper_bgcolor='#fff9c4', plot_bgcolor='#fff9c4')
        st.plotly_chart(line_fig, use_container_width=True)

    st.markdown("""
    🔄 [Open Pie Chart in New Tab](?view=pie) | [Open Line Chart in New Tab](?view=line)
    """)

    # 🔒 SECRET ADMIN SECTION: Reveal Winner, Payouts & Reset (FIXED)
    with st.expander("🔒 Admin: Rally for Impact, Payouts & Reset"):
        admin_pass = st.text_input("Enter admin password:", type="password")

        if admin_pass == "mysecret123":
            st.header("🎁 Rally for Impact - Announce Winner")
            
            # FIX: Variable naming (was 'gender', now 'team')
            selected_team = st.selectbox("Which Team Won?", ["-- Select --", "Team 1", "Team 2"])
            
            if selected_team != "-- Select --":
                st.session_state.which_team = selected_team
                st.success(f"🎉 Winner Team: {selected_team}")

            if st.session_state.which_team:
                winning_team = st.session_state.which_team
                winners = st.session_state.bets[st.session_state.bets['Choice'] == winning_team]
                total_winner_bets = winners['Bet'].sum()

                payouts = []
                for _, row in st.session_state.bets.iterrows():
                    if row['Choice'] == winning_team and total_winner_bets > 0:
                        payout = row['Bet'] * total_pool / total_winner_bets
                        payout = round(payout / 100000) * 100000  # Round to nearest 100k
                    else:
                        payout = 0
                    payouts.append(payout)

                result = st.session_state.bets.copy()
                result['Payout (Rupiah)'] = payouts

                st.header("💰 Final Payouts")
                result_display = result.copy()
                result_display['Bet'] = result_display['Bet'].apply(lambda x: f"Rp {x:,.0f}")
                result_display['Payout (Rupiah)'] = result_display['Payout (Rupiah)'].apply(lambda x: f"Rp {x:,.0f}")
                st.dataframe(result_display, use_container_width=True)

                st.write(f"🏆 Total Pool: Rp {total_pool:,.0f} distributed to winners.")

                # Download Excel
                towrite = BytesIO()
                with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
                    result.to_excel(writer, index=False, sheet_name='Payouts')
                towrite.seek(0)

                st.download_button(
                    label="📥 Download Payouts as Excel",
                    data=towrite,
                    file_name="RallyforImpact_Payouts.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            st.header("🗑️ Reset Market")
            if st.button("🔄 Reset Everything"):
                st.session_state.bets = pd.DataFrame(columns=['Name', 'Choice', 'Bet'])
                st.session_state.which_team = None
                st.session_state.odds_history = pd.DataFrame(columns=['Timestamp', 'Team 1', 'Team 2'])
                save_bets(st.session_state.bets)
                save_odds(st.session_state.odds_history)
                st.success("✅ Market reset successfully!")
                st.rerun()
        else:
            if admin_pass:  # Only show message if they tried to enter password
                st.error("❌ Incorrect password.")
            else:
                st.info("🔑 Enter the admin password to access this section.")
