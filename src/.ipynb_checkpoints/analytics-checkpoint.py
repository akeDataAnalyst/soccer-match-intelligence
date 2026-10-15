import pandas as pd
import numpy as np

class MatchLensAnalytics:
    """Core analytical aggregation functions for match events and player performance."""
    
    @staticmethod
    def get_match_kpis(df_events: pd.DataFrame) -> dict:
        """Compute high-level match key performance indicators."""
        total_events = len(df_events)
        total_goals = int((df_events['is_goal'] == True).sum()) if 'is_goal' in df_events.columns else 0
        total_cards = int((df_events['is_card'] == True).sum()) if 'is_card' in df_events.columns else 0
        total_subs = int((df_events['is_substitution'] == True).sum()) if 'is_substitution' in df_events.columns else 0
        
        return {
            "total_events": total_events,
            "total_goals": total_goals,
            "total_cards": total_cards,
            "total_subs": total_subs
        }

    @staticmethod
    def get_goal_distribution(df_events: pd.DataFrame) -> pd.DataFrame:
        """Aggregate goals by 15-minute time intervals."""
        if 'is_goal' not in df_events.columns or 'time_bucket' not in df_events.columns:
            return pd.DataFrame(columns=['time_bucket', 'goal_count'])
        
        df_goals = df_events[df_events['is_goal'] == True]
        if df_goals.empty:
            return pd.DataFrame(columns=['time_bucket', 'goal_count'])
            
        return df_goals.groupby('time_bucket').size().reset_index(name='goal_count')

    @staticmethod
    def get_discipline_distribution(df_events: pd.DataFrame) -> pd.DataFrame:
        """Aggregate disciplinary cards by time interval and team for risk profiling."""
        if 'is_card' not in df_events.columns or 'time_bucket' not in df_events.columns:
            return pd.DataFrame(columns=['time_bucket', 'team', 'card_count'])
            
        df_cards = df_events[df_events['is_card'] == True]
        if df_cards.empty:
            return pd.DataFrame(columns=['time_bucket', 'team', 'card_count'])
            
        return df_cards.groupby(['time_bucket', 'team']).size().reset_index(name='card_count')

    @staticmethod
    def get_player_leaderboard(df_events: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """Rank players by total event actions, shots, and goals."""
        if df_events.empty:
            return pd.DataFrame()
            
        # Ensure flag columns exist safely
        df = df_events.copy()
        if 'is_goal' not in df.columns:
            df['is_goal'] = False
        if 'is_card' not in df.columns:
            df['is_card'] = False
            
        df_players = df.groupby(['team', 'player']).agg(
            total_events=('event_id', 'count'),
            shots=('type', lambda x: (x == 'Shot').sum()),
            goals=('is_goal', 'sum'),
            cards=('is_card', 'sum')
        ).reset_index()
        
        # Filter out unassigned/null players and sort
        df_players = df_players[df_players['player'].notna()]
        return df_players.sort_values(by='total_events', ascending=False).head(top_n)