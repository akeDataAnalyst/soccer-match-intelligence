import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
import os

# Ensure root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.transformer import MatchLensTransformer
from src.reporter import MatchLensReporter
from src.analytics import MatchLensAnalytics

# Page Configuration
st.set_page_config(
    page_title="MatchLens | Soccer Match Intelligence",
    page_icon="⚽",
    layout="wide"
)

# Initialize Services
@st.cache_resource
def get_services():
    transformer = MatchLensTransformer(raw_data_dir="data/raw")
    reporter = MatchLensReporter(reports_dir="reports")
    return transformer, reporter

transformer, reporter = get_services()

# App Header
st.title("⚽ Soccer Match Intelligence & Reporting")
st.markdown("Advanced post-match analytics, risk intelligence, and automated storytelling powered by StatsBomb data.")

# Match Selection
st.sidebar.header("Match Selection")
events_dir = Path("data/raw/events")

if events_dir.exists():
    cached_match_files = list(events_dir.glob("*.json"))
    cached_match_ids = [f.stem for f in cached_match_files]
else:
    cached_match_ids = []

if not cached_match_ids:
    st.warning("No cached match JSONs found under `data/raw/events/`. Please run your ingestion notebook first!")
    st.stop()

selected_match_id = st.sidebar.selectbox("Select Match ID:", cached_match_ids)
match_id_int = int(selected_match_id)

# Load and Transform Data
@st.cache_data
def load_and_process(m_id):
    df_raw = transformer.load_match_events(m_id)
    df_clean = transformer.engineer_features(df_raw)
    return df_clean

with st.spinner(f"Processing event stream for Match ID {match_id_int}..."):
    df_events = load_and_process(match_id_int)

teams = df_events['team'].dropna().unique()
team_a = teams[0] if len(teams) > 0 else "Home Team"
team_b = teams[1] if len(teams) > 1 else "Away Team"

st.sidebar.markdown(f"**Fixture:** {team_a} vs {team_b}")

# TAB NAVIGATION 
tab1, tab2, tab3, tab4 = st.tabs([
    "Match Overview & Narrative", 
    "Goals & Timing", 
    "Discipline & Risk", 
    "Substitution Impact"
])

with tab1:
    st.subheader(f"Executive Match Summary: {team_a} vs {team_b}")
    
    # Generate Narrative
    narrative = reporter.generate_match_narrative(match_id_int, df_events)
    st.info(narrative)
    
    # KPI Metrics using MatchLensAnalytics
    kpis = MatchLensAnalytics.get_match_kpis(df_events)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Match Events", f"{kpis['total_events']:,}")
    col2.metric("Goals Scored", kpis['total_goals'])
    col3.metric("Disciplinary Cards", kpis['total_cards'])
    col4.metric("Substitutions", kpis['total_subs'])
    
    st.markdown("---")
    st.subheader("Match Rhythm & Flow Intensity")
    
    # Match Flow Chart
    df_events['match_flow_bin'] = pd.cut(
        df_events['minute'], 
        bins=range(0, 121, 10), 
        right=False, 
        labels=[f"{i}-{i+9}'" for i in range(0, 120, 10)]
    )
    match_flow = df_events.groupby(['match_flow_bin', 'team']).size().reset_index(name='event_volume')
    
    fig_flow = px.line(
        match_flow, x='match_flow_bin', y='event_volume', color='team', markers=True,
        title="Event Volume | Intensity Wave Over Match Duration",
        labels={'match_flow_bin': 'Match Intervals', 'event_volume': 'Event Volume'}
    )
    st.plotly_chart(fig_flow, use_container_width=True)

with tab2:
    st.subheader("Goal & Scoring Interval Analysis")
    df_goals = df_events[df_events['is_goal'] == True].copy()
    
    if not df_goals.empty:
        st.dataframe(df_goals[['minute', 'team', 'player', 'shot_statsbomb_xg', 'half']], use_container_width=True)
        
        goal_intervals = MatchLensAnalytics.get_goal_distribution(df_events)
        fig_goals = px.bar(
            goal_intervals, x='time_bucket', y='goal_count',
            title="Goals Scored by 15-Minute Time Interval",
            color='goal_count', color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_goals, use_container_width=True)
    else:
        st.info("No goal events recorded in this match payload.")

with tab3:
    st.subheader("Disciplinary Risk & Card Timing Analysis")
    df_cards = df_events[df_events['is_card'] == True].copy()
    
    if not df_cards.empty:
        st.dataframe(df_cards[['minute', 'team', 'player', 'time_bucket', 'half']], use_container_width=True)
        
        card_intervals = MatchLensAnalytics.get_discipline_distribution(df_events)
        fig_cards = px.bar(
            card_intervals, x='time_bucket', y='card_count', color='team', barmode='group',
            title="Card Distribution across Match Segments"
        )
        st.plotly_chart(fig_cards, use_container_width=True)
    else:
        st.info("No disciplinary cards recorded in this match payload.")

with tab4:
    st.subheader("Substitution Impact & Tactical Windows")
    df_subs = df_events[df_events['is_substitution'] == True].copy()
    
    if not df_subs.empty:
        sub_records = []
        for _, sub in df_subs.iterrows():
            sub_min = sub['minute']
            sub_team = sub['team']
            sub_player = sub['player']
            replacement = sub.get('sub_replacement', 'Unknown')
            
            window_events = df_events[
                (df_events['team'] == sub_team) & 
                (df_events['minute'] > sub_min) & 
                (df_events['minute'] <= sub_min + 15)
            ]
            shots_in_window = len(window_events[window_events['type'] == 'Shot'])
            
            sub_records.append({
                'Substitution Minute': sub_min,
                'Team': sub_team,
                'Player Off': sub_player,
                'Player On': replacement,
                'Team Shots (+15m Window)': shots_in_window
            })
            
        df_sub_summary = pd.DataFrame(sub_records)
        st.dataframe(df_sub_summary, use_container_width=True)
    else:
        st.info("No substitutions recorded in this match sample.")

# Footer Export Action & Developer Credit
st.sidebar.markdown("---")
if st.sidebar.button("Export Markdown Match Report"):
    report_file = reporter.export_match_report(match_id_int, df_events)
    st.sidebar.success(f"Report saved to `{report_file}`")

st.sidebar.markdown("---")
st.sidebar.caption("**Developed by Aklilu Abera | Data Analyst**")