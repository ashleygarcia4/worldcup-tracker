import os
import psycopg2
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

app = FastAPI()

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.get("/")
def home():
    return {"message": "World Cup Tracker API is running"}

@app.get("/matches")
def get_matches(team: str = None):
    conn = get_connection()
    cur = conn.cursor()

    if team:
        cur.execute(
            "SELECT home_team, away_team, status, match_date, home_score, away_score "
            "FROM matches WHERE home_team ILIKE %s OR away_team ILIKE %s",
            (f"%{team}%", f"%{team}%")
        )
    else:
        cur.execute(
            "SELECT home_team, away_team, status, match_date, home_score, away_score FROM matches"
        )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "home_team": row[0],
            "away_team": row[1],
            "status": row[2],
            "match_date": row[3].isoformat() if row[3] else None,
            "home_score": row[4],
            "away_score": row[5],
        })
    return results