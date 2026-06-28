# World Cup Live Tracker & Predictor

A data pipeline + REST API that ingests live World Cup match data, stores it
in PostgreSQL, and serves match data and outcome predictions via FastAPI.
Deployed on AWS using RDS (database) and EC2 (API server).

## Architecture
1. **Ingestion**: Python script pulls match data from the football-data.org
   API and upserts it into PostgreSQL.
2. **Storage**: PostgreSQL database hosted on **AWS RDS**, with a `matches`
   table storing match results and schedules.
3. **API**: FastAPI serves endpoints to query matches and get ML-based
   outcome predictions, deployed on an **AWS EC2** instance.
4. **ML**: A Random Forest classifier trained on team performance stats
   (avg goals for/against, win rate) predicts match outcomes.

## Tech Stack
Python, PostgreSQL, AWS RDS, AWS EC2, FastAPI, scikit-learn, pandas, psycopg2

## Live Deployment
The API runs on an AWS EC2 instance and connects to a PostgreSQL database
hosted on AWS RDS. Database connections use SSL (`sslmode=require`), and
network access between EC2 and RDS is restricted using AWS security groups
(the API instance's security group is explicitly allowed on RDS's inbound
rules, rather than opening the database to the public internet).

## Endpoints
- `GET /matches` — list all matches (optional `?team=` filter)
- `GET /predict?home_team=X&away_team=Y` — predict match outcome with probability breakdown

## Setup (local development)
```bash
git clone https://github.com/ashleygarcia4/worldcup-tracker.git
cd worldcup-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with:
```
API_KEY=your_football_data_org_key
DB_NAME=postgres
DB_USER=postgres
DB_HOST=your_rds_endpoint
DB_PORT=5432
DB_PASSWORD=your_rds_password
```

Run ingestion: `python WorldCupLiveTracker.py`
Train model: `python train_model.py`
Start API: `uvicorn main:app --reload`

## Deploying to AWS (EC2)
1. Launch an EC2 instance (Amazon Linux 2023, t2/t3.micro for free tier).
2. Open inbound port 8000 (Custom TCP) on the EC2 security group.
3. On the RDS security group, add an inbound rule allowing PostgreSQL (5432)
   traffic from the EC2 instance's security group, so the two can communicate
   privately within AWS rather than over the public internet.
4. SSH (or use EC2 Instance Connect) into the instance, clone this repo,
   create a `.env` file with your RDS connection details, install
   dependencies, and run:
   ```bash
   uvicorn main:app --host 0.0.0.0 --reload
   ```
5. Access the API at `http://<EC2_PUBLIC_IP>:8000/matches`.

## Model Limitations
This prediction model is trained only on completed matches available
under football-data.org's free-tier API, which restricts historical access
to the current season. With a larger sample (multiple World Cups or full
league seasons), accuracy would likely improve substantially. The model
also shows a meaningful gap between training and test accuracy on this
small dataset (a sign of overfitting), so results should be read as a
proof of concept rather than a production-grade predictor.