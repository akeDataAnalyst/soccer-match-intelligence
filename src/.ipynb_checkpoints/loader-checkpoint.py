import os
import json
import requests
from pathlib import Path
import pandas as pd

class MatchLensLoader:
    """Automated ingestion engine for StatsBomb Open Data."""
    
    def __init__(self, raw_data_dir: str = "data/raw"):
        self.raw_dir = Path(raw_data_dir)
        self.base_url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
        
    def download_competitions(self) -> pd.DataFrame:
        """Download global competitions index and save locally."""
        url = f"{self.base_url}/competitions.json"
        print(f"Fetching competitions metadata from StatsBomb...")
        response = requests.get(url)
        response.raise_for_status()
        
        competitions = response.json()
        
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        comp_path = self.raw_dir / "competitions.json"
        with open(comp_path, "w", encoding="utf-8") as f:
            json.dump(competitions, f, indent=4)
            
        print(f"Successfully saved competitions index to {comp_path}")
        return pd.DataFrame(competitions)

    def download_matches(self, competition_id: int, season_id: int) -> pd.DataFrame:
        """Download match schedules for a specific competition and season."""
        url = f"{self.base_url}/matches/{competition_id}/{season_id}.json"
        print(f"Fetching matches for Competition ID: {competition_id}, Season ID: {season_id}...")
        response = requests.get(url)
        response.raise_for_status()
        
        matches = response.json()
        
        match_dir = self.raw_dir / "matches" / str(competition_id)
        match_dir.mkdir(parents=True, exist_ok=True)
        match_path = match_dir / f"{season_id}.json"
        
        with open(match_path, "w", encoding="utf-8") as f:
            json.dump(matches, f, indent=4)
            
        print(f"Successfully saved match schedules to {match_path}")
        return pd.DataFrame(matches)

    def download_match_payloads(self, match_id: int):
        """Download raw event and lineup JSON payloads for a specific match ID."""
        events_url = f"{self.base_url}/events/{match_id}.json"
        lineups_url = f"{self.base_url}/lineups/{match_id}.json"
        
        events_dir = self.raw_dir / "events"
        lineups_dir = self.raw_dir / "lineups"
        events_dir.mkdir(parents=True, exist_ok=True)
        lineups_dir.mkdir(parents=True, exist_ok=True)
        
        # Download events
        res_events = requests.get(events_url)
        if res_events.status_code == 200:
            with open(events_dir / f"{match_id}.json", "w", encoding="utf-8") as f:
                json.dump(res_events.json(), f)
                
        # Download lineups
        res_lineups = requests.get(lineups_url)
        if res_lineups.status_code == 200:
            with open(lineups_dir / f"{match_id}.json", "w", encoding="utf-8") as f:
                json.dump(res_lineups.json(), f)
                
        print(f"Cached raw JSON payloads for Match ID {match_id} under data/raw/")