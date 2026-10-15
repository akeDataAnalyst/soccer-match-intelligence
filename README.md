# Soccer Match Intelligence & Automated Reporting System

## Description
MatchLens is an end-to-end sports analytics and automated reporting engine designed to process raw soccer event data, extract tactical insights, track disciplinary and betting-risk indicators, and generate broadcast-ready narratives. Built to mirror the operational workflows of professional sports data providers (such as Stats Perform), MatchLens bridges raw JSON event streams and high-impact media storytelling.

---

## The Problem
In modern sports media, scouting, and broadcast operations, analysts face major friction points:
* **Data Ingestion Bottlenecks:** Raw event streams (like StatsBomb JSON payloads) are deeply nested, heavy, and complex to parse manually under tight pre-match and post-match deadlines.
* **Manual Reporting Delay:** Crafting tactical summaries, disciplinary risk profiles, and post-match narratives requires hours of manual cross-referencing across events, lineups, and timestamps.
* **Lack of Real-Time Tactical Visibility:** Identifying critical momentum shifts (such as performance changes within 15 minutes of tactical substitutions) is often based on subjective observation rather than automated data tracking.

---

## The Solution
MatchLens delivers a fully automated analytics pipeline and interactive command center that solves these challenges:
* Automated Data Ingestion: Programmatically connects to open sports repositories, fetches match schedules, and caches raw event and lineup payloads locally.
* Advanced Feature Engineering: Transforms flat event records into structured analytical tables enriched with **15-minute time intervals**, half labels, and key event flags (goals, cards, substitutions).
* Tactical & Risk Windows: Automatically measures post-substitution impact windows ($+15\text{ min}$) and highlights high-risk disciplinary periods for predictive risk assessment.
* Interactive Command Center: Provides a multi-tab Streamlit dashboard for instant visual inspection of match rhythm, goal distributions, and player involvements.

---

## Automated Reporting & Storytelling
MatchLens features a built-in automated reporter module (`src/reporter.py`) that programmatically reads event streams to craft professional, broadcast-ready match narratives. 
* Dynamic Summaries: Instantly computes goal counts, second-half scoring shares, card distributions by team, and substitution frequencies.
* Markdown Export: Generates and exports comprehensive audit-ready Markdown reports (`reports/match_report_[ID].md`) with structured executive summaries and key statistical tables for media publication.

---

## Tech Stack
* Core Language: Python 3.x
* Data Processing & Manipulation: Pandas, NumPy, PyArrow
* Interactive Frontend: Streamlit
* Data Visualization: Plotly
* Data Source: StatsBomb Open Data API

---

## Project Structure
```text
matchlens/
├── data/
│   ├── raw/               # Cached raw JSON event and lineup payloads
│  
├── notebooks/             # Step-by-step analytical Jupyter notebooks
├── src/
│   ├── loader.py          # Automated API ingestion engine
│   ├── transformer.py     # Feature engineering & timeline structuring
│   ├── analytics.py       # Core metric aggregation functions
│   └── reporter.py        # Automated narrative generator & report exporter
├── app/
│   └── app.py             # Streamlit Analytics Command Center
├── reports/               # Exported markdown match narratives and logs
├── requirements.txt       # Project dependencies
└── README.md
