# mei_monitor

This project reads configuration from a .env file (optional) using python-dotenv. Copy `.env.example` to `.env` and edit values for your environment.

Quick start:

1. Create and edit `.env`:
   cp .env.example .env
   # edit .env and set SECRET_KEY, TELEGRAM_BOT_TOKEN, etc.

2. Install dependencies:
   pip install -r requirements.txt

3. Run the server:
   python manage.py runserver

Notes:
- In production set DEBUG=False and configure ALLOWED_HOSTS.
- You can use DATABASE_URL to configure Postgres/MySQL (requires `dj-database-url`).
