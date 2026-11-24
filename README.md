Local Windows test:
1. cd backend
2. py -m venv venv
3. .\\venv\\Scripts\\Activate.ps1
4. pip install -r requirements.txt
5. Copy-Item .env.example .env and edit JWT_SECRET
6. uvicorn main:app --reload --port 8000
Open http://127.0.0.1:8000/docs

For EC2/Linux use python3 -m venv venv; source venv/bin/activate; pip install -r requirements.txt;
then run uvicorn main:app --host 127.0.0.1 --port 8000 behind Nginx/HTTPS.
SQLite is for testing. Before production use PostgreSQL/RDS, a strong secret manager,
HTTPS, rate limiting, email verification, password reset, backups and migrations.
