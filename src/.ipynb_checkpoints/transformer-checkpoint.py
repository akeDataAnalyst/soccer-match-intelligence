import json
from pathlib import Path
import pandas as pd
import numpy as np

class MatchLensTransformer:
    """Transforms raw StatsBomb match JSONs into structured analytical event tables."""
    
    def __init__(self, raw_data_dir: str = "data/raw"):
        self.raw_dir = Path(raw_data_dir)
        
    def load_match_events(self, match_id: int) -> pd.DataFrame:
        """Load raw events JSON for a specific match into a flat Pandas DataFrame."""
        event_path = self.raw_dir / "events" / f"{match_id}.json"
        if not event_path.exists():
            raise FileNotFoundError(f"Raw events file not found for match ID {match_id} at {event_path}")
            
        with open(event_path, "r", encoding="utf-8") as f:
            events = json.load(f)
            
        # Flatten basic event structure
        flattened = []
        for ev in events:
            row = {
                "match_id": match_id,
                "event_id": ev.get("id"),
                "index": ev.get("index"),
                "period": ev.get("period"),
                "timestamp": ev.get("timestamp"),
                "minute": ev.get("minute"),
                "second": ev.get("second"),
                "type": ev.get("type", {}).get("name"),
                "team": ev.get("team", {}).get("name"),
                "player": ev.get("player", {}).get("name"),
                "possession_team": ev.get("possession_team", {}).get("name")
            }
            
            # Extract nested sub-types or specific event attributes
            sub_type = ev.get("sub_type")
            if sub_type:
                row["sub_type"] = sub_type.get("name")
                
            # Extract shot details if available
            if row["type"] == "Shot":
                shot = ev.get("shot", {})
                row["shot_outcome"] = shot.get("outcome", {}).get("name")
                row["shot_statsbomb_xg"] = shot.get("statsbomb_xg")
                
            # Extract card details if available
            if row["type"] == "Foul Committed":
                card = ev.get("foul_committed", {}).get("card")
                if card:
                    row["card_type"] = card.get("name")
                    
            # Extract substitution details if available
            if row["type"] == "Substitution":
                replacement = ev.get("substitution", {}).get("replacement", {})
                row["sub_replacement"] = replacement.get("name")

            flattened.append(row)
            
        return pd.DataFrame(flattened)

    def engineer_features(self, df_events: pd.DataFrame) -> pd.DataFrame:
        """Apply analytical feature engineering (time buckets, half labels, key flags)."""
        df = df_events.copy()
        
        # 1. Period / Half Label
        df['half'] = df['period'].map({1: 'First Half', 2: 'Second Half', 3: 'Extra Time 1', 4: 'Extra Time 2'})
        
        # 2. 15-Minute Time Buckets
        def assign_time_bucket(minute):
            if pd.isna(minute):
                return "Unknown"
            elif minute <= 15:
                return "00-15"
            elif minute <= 30:
                return "16-30"
            elif minute <= 45:
                return "31-45+"
            elif minute <= 60:
                return "46-60"
            elif minute <= 75:
                return "61-75"
            else:
                return "76-90+"
                
        df['time_bucket'] = df['minute'].apply(assign_time_bucket)
        
        # 3. Key Event Flags
        df['is_goal'] = (df['type'] == 'Shot') & (df.get('shot_outcome') == 'Goal')
        df['is_card'] = df['type'].isin(['Bad Behaviour']) | (df['card_type'].notna() if 'card_type' in df.columns else False)
        df['is_substitution'] = (df['type'] == 'Substitution')
        
        return df