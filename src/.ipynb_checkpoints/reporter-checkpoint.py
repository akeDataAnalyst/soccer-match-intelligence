import pandas as pd
from pathlib import Path

class MatchLensReporter:
    """Generates automated natural-language match narratives and structured Markdown reports."""
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_match_narrative(self, match_id: int, df_events: pd.DataFrame) -> str:
        """Programmatically crafts a broadcast-style one-paragraph match narrative."""
        teams = df_events['team'].dropna().unique()
        if len(teams) < 2:
            return f"Match {match_id}: Insufficient team data to generate a narrative."
            
        team_a, team_b = teams[0], teams[1]
        
        # Extract metrics
        goals = df_events[df_events['is_goal'] == True]
        cards = df_events[df_events['is_card'] == True]
        subs = df_events[df_events['is_substitution'] == True]
        
        goal_h2 = len(goals[goals['period'] == 2])
        
        card_counts = cards['team'].value_counts() if not cards.empty else pd.Series()
        team_a_cards = card_counts.get(team_a, 0)
        team_b_cards = card_counts.get(team_b, 0)
        
        # Crafting dynamic broadcast narrative
        narrative = (
            f"**Match Narrative (Match ID: {match_id})**: "
            f"The fixture between {team_a} and {team_b} demonstrated high competitive intensity. "
            f"A total of {len(goals)} goal(s) were recorded, with {goal_h2} coming in the second half. "
            f"Disciplinary oversight noted {team_a_cards} card(s) for {team_a} and {team_b_cards} card(s) for {team_b}, "
            f"while both sides utilized a combined {len(subs)} tactical substitution(s) to shift match momentum."
        )
        return narrative

    def export_match_report(self, match_id: int, df_events: pd.DataFrame) -> str:
        """Export a comprehensive Markdown summary report for the match."""
        narrative = self.generate_match_narrative(match_id, df_events)
        
        report_path = self.reports_dir / f"match_report_{match_id}.md"
        
        total_goals = len(df_events[df_events['is_goal'] == True])
        total_cards = len(df_events[df_events['is_card'] == True])
        total_subs = len(df_events[df_events['is_substitution'] == True])
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# MatchLens Post-Match Report | Match ID: {match_id}\n\n")
            f.write(f"## Executive Summary\n{narrative}\n\n")
            f.write(f"## Key Match Statistics\n")
            f.write(f"| Metric | Count |\n")
            f.write(f"| :--- | :--- |\n")
            f.write(f"| **Total Events Processed** | {len(df_events)} |\n")
            f.write(f"| **Goals Scored** | {total_goals} |\n")
            f.write(f"| **Disciplinary Cards** | {total_cards} |\n")
            f.write(f"| **Substitutions Made** | {total_subs} |\n\n")
            f.write(f"---\n*Generated automatically by MatchLens Intelligence Engine.*")
            
        print(f"Match report successfully exported to {report_path}")
        return str(report_path)