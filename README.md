# World Cup Live Tracker & Predictor

A data pipeline + REST API that ingests live World Cup match data, stores it
in PostgreSQL, and serves match data and outcome predictions via FastAPI.

## Architecture
1. **Ingestion**: Python script pulls match data from the football-data.org
   API and upserts it into PostgreSQL.
2. **Storage**: PostgreSQL database with a `matches` table.
3. **API**: FastAPI serves endpoints to query matches and get ML-based
   outcome predictions.
4. **ML**: A Random Forest classifier trained on team performance stats
   (avg goals for/against, win rate) predicts match outcomes.

## Tech Stack
Python, PostgreSQL, FastAPI, scikit-learn, pandas, psycopg2

## Endpoints
- `GET /matches` — list all matches (optional `?team=` filter)
- `GET /predict?home_team=X&away_team=Y` — predict match outcome with probability breakdown

## Setup
\`\`\`bash
git clone https://github.com/ashleygarcia4/worldcup-tracker.git
cd worldcup-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

Create a `.env` file with:
\`\`\`
API_KEY=your_football_data_org_key
DB_NAME=worldcup
DB_USER=your_postgres_user
DB_HOST=localhost
DB_PORT=5432
\`\`\`

Run ingestion: `python WorldCupLiveTracker.py`
Train model: `python train_model.py`
Start API: `uvicorn main:app --reload`

## Model Limitations
This prediction model is trained only on the 42 completed matches available
under football-data.org's free-tier API, which restricts historical access
to the current season. With a larger sample (multiple World Cups or full
league seasons), accuracy would likely improve substantially. Test accuracy
on this dataset was 63.6%, evaluated on an 11-match holdout set — a result
that should be read as a proof of concept rather than a production-grade
predictor, given the small sample size.
