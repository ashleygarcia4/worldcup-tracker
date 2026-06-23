import os
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.football-data.org/v4"
headers = {"X-Auth-Token": API_KEY}

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def get_world_cup_matches():
    url = f"{BASE_URL}/competitions/WC/matches"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def save_matches_to_db(matches):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    for match in matches:
        api_match_id = match["id"]
        home_team = (match.get("homeTeam") or {}).get("name") or "TBD"
        away_team = (match.get("awayTeam") or {}).get("name") or "TBD"
        status = match["status"]
        match_date = match["utcDate"]
        home_score = match["score"]["fullTime"]["home"]
        away_score = match["score"]["fullTime"]["away"]

        cur.execute("""
            INSERT INTO matches (api_match_id, home_team, away_team, status, match_date, home_score, away_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (api_match_id)
            DO UPDATE SET
                status = EXCLUDED.status,
                home_score = EXCLUDED.home_score,
                away_score = EXCLUDED.away_score;
        """, (api_match_id, home_team, away_team, status, match_date, home_score, away_score))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Saved {len(matches)} matches to the database.")

if __name__ == "__main__":
    data = get_world_cup_matches()
    matches = data.get("matches", [])
    print(f"Found {len(matches)} matches from API")
    save_matches_to_db(matches)