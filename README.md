# Auto interview and evaluation parallel system

## Description

Auto Interviewer is an autonomous interview agent which can perform interviews for any position. It has two processes
which run in parallel to interview and evaluate and write to database in parallel asynchronously. It features threading
for parallelization a queue system and observer pattern for automatic notification of the evaluator of every Q and A
pairs. It writes to a sqlite database and save on gg sheets.

## Features

- [x] Interviewer
- [x] Evaluator
- [x] Database local
- [x] Google Sheets
- [x] Threading
- [x] Queue
- [x] Observer Pattern
- [x] streamlit

## Environment

- Python 3.10.13

## Installation

### Requires

```bash
pip install -r requirements.txt
```

Before Deployment:

- Config .streamlit/secrets.toml file
- Create a google service account and download the json file and config the .streamlit/secrets.toml file with the path
  to the json file.
- Create a google sheet and share it with the email in the json file.
- Create a .streamlit/secrets.toml file and add the following:

```bash
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/xxx/edit#gid=0"
type = "service_account"
project_id = "chat-with-gg-meet"
private_key_id = "xxx"
private_key = "xxx"
client_email = "xxx@xxx.iam.gserviceaccount.com"
client_id = "xxx"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "xxx"
```

## Run app ⛄️

Run cli app:

```bash
python main.py

```

Run app with streamlit:

```bash
streamlit run app.py
# OR
sh bin/start.sh
```

## Run with Docker 🐳

Docker build and run with Dockerfile:

```bash
docker build -t auto_interview_app .       # Build the docker image
docker run -p 5001:5001 auto_interview_app # Run the docker image

```

Run with docker-compose:

```bash
docker compose up --build -d
```

 - GG Sheets: https://docs.google.com/spreadsheets/d/1bFwQc55UwS2axNfwHvA4D0Q0NKi1SO2JisHRdZczqgQ/edit#gid=998067017
 - Youtube: https://www.youtube.com/watch?v=LLFkEv4dMiU