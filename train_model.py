import os
import pandas as pd
import psycopg2
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split


load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def load_finished_matches():
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(
        "SELECT home_team, away_team, home_score, away_score "
        "FROM matches WHERE status = 'FINISHED' AND home_team != 'TBD'",
        conn
    )
    conn.close()
    return df

def build_team_stats(df):
    stats = {}
    for team in pd.unique(df[["home_team", "away_team"]].values.ravel()):
        home_games = df[df.home_team == team]
        away_games = df[df.away_team == team]

        goals_for = home_games.home_score.sum() + away_games.away_score.sum()
        goals_against = home_games.away_score.sum() + away_games.home_score.sum()
        games_played = len(home_games) + len(away_games)

        wins = ((home_games.home_score > home_games.away_score).sum() +
                (away_games.away_score > away_games.home_score).sum())

        stats[team] = {
            "avg_goals_for": goals_for / games_played if games_played else 0,
            "avg_goals_against": goals_against / games_played if games_played else 0,
            "win_rate": wins / games_played if games_played else 0,
        }
    return stats

def outcome(row):
    if row.home_score > row.away_score:
        return "HOME_WIN"
    elif row.home_score < row.away_score:
        return "AWAY_WIN"
    return "DRAW"

def build_training_data(df, stats):
    rows = []
    for _, row in df.iterrows():
        h, a = stats[row.home_team], stats[row.away_team]
        rows.append({
            "home_avg_goals_for": h["avg_goals_for"],
            "home_avg_goals_against": h["avg_goals_against"],
            "home_win_rate": h["win_rate"],
            "away_avg_goals_for": a["avg_goals_for"],
            "away_avg_goals_against": a["avg_goals_against"],
            "away_win_rate": a["win_rate"],
            "outcome": outcome(row),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = load_finished_matches()
    print(f"Training on {len(df)} finished matches")

    stats = build_team_stats(df)
    training_df = build_training_data(df, stats)

    X = training_df.drop(columns=["outcome"])
    y = training_df["outcome"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.25, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, max_depth=4, random_state=42)
    model.fit(X_train, y_train)

    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)

    print(f"Training accuracy: {train_acc:.2%}")
    print(f"Test accuracy: {test_acc:.2%}")

    # Refit on all data for the final saved model (after we've validated the approach)
    model.fit(X, y_encoded)
    joblib.dump(model, "model.joblib")
    joblib.dump(le, "label_encoder.joblib")
    joblib.dump(stats, "team_stats.joblib")
    print("Final model trained on full dataset and saved.")