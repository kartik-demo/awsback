Local Windows test:
1. cd backend
2. py -m venv venv
3. .\\venv\\Scripts\\Activate.ps1
4. pip install -r requirements.txt
5. Copy-Item .env.example .env and edit JWT_SECRET
6. uvicorn main:app --reload --port 8000
Open http://127.0.0.1:8000/docs

Generate a strong local JWT secret with `py -c "import secrets; print(secrets.token_urlsafe(48))"` and keep the value in `.env`. The application loads `.env` and refuses to start with a missing or placeholder key.

For EC2/Linux use python3 -m venv venv; source venv/bin/activate; pip install -r requirements.txt;
then run uvicorn main:app --host 127.0.0.1 --port 8000 behind Nginx/HTTPS.
SQLite is for testing. Before production use PostgreSQL/RDS, a strong secret manager,
HTTPS, rate limiting, email verification, password reset, backups and migrations.

## GitHub Actions

The backend uses Python 3.14. `.github/workflows/ci.yml` runs on pushes to `main` and pull requests targeting `main`. It installs `requirements.txt` and `requirements-dev.txt`, caches pip dependencies, checks syntax, runs Ruff and pytest, and validates that the FastAPI app imports. Tests use a temporary SQLite database and a random test-only JWT key.

`.github/workflows/deploy.yml` is prepared for EC2. Automatic deployment requires a successful CI push for the current `main` commit; manual deployment also requires an explicit confirmation and a successful CI run for the current `main`. The deployment job remains skipped unless repository variable `DEPLOY_ENABLED` is set to `true`. It uses the `production` GitHub Environment, so configure required reviewers there if an approval gate is desired.

Before enabling deployment, create these GitHub Actions secrets:

- `EC2_HOST` — EC2 public DNS name or IPv4 address.
- `EC2_USER` — non-root SSH user.
- `EC2_SSH_PORT` — SSH port number.
- `EC2_SSH_PRIVATE_KEY` — private key for that user.
- `EC2_KNOWN_HOSTS` — verified SSH host-key line for that host (use `[host]:port` for a non-default port).

Create these GitHub Actions variables:

- `DEPLOY_ENABLED` — leave unset or `false` until EC2 is ready; set to `true` to enable.
- `DEPLOY_PATH` — absolute application directory on EC2.
- `SYSTEMD_SERVICE` — systemd unit name to restart.
- `HEALTH_CHECK_URL` — public health endpoint URL.

The EC2 deploy user must be able to write `DEPLOY_PATH`, create/use its `.venv`, and run non-interactive `sudo systemctl restart` and `sudo systemctl is-active` for the configured service. The workflow excludes `.env` and virtual environments from the release archive, installs updated dependencies, restarts the service, and checks health. No deployment is attempted until the secrets and variables are configured.

## GitHub Actions

The backend uses Python 3.14. `.github/workflows/ci.yml` runs on pushes to `main` and pull requests targeting `main`. It installs `requirements.txt` and `requirements-dev.txt`, caches pip dependencies, checks syntax, runs Ruff and pytest, and validates that the FastAPI app imports. Tests use a temporary SQLite database and a random test-only JWT key.

`.github/workflows/deploy.yml` is prepared for EC2. Automatic deployment requires a successful CI push for the current `main` commit; manual deployment also requires an explicit confirmation and a successful CI run for the current `main`. The deployment job remains skipped unless repository variable `DEPLOY_ENABLED` is set to `true`. It uses the `production` GitHub Environment, so configure required reviewers there if an approval gate is desired.

Before enabling deployment, create these GitHub Actions secrets:

- `EC2_HOST` — EC2 public DNS name or IPv4 address.
- `EC2_USER` — non-root SSH user.
- `EC2_SSH_PORT` — SSH port number.
- `EC2_SSH_PRIVATE_KEY` — private key for that user.
- `EC2_KNOWN_HOSTS` — verified SSH host-key line for that host (use `[host]:port` for a non-default port).

Create these GitHub Actions variables:

- `DEPLOY_ENABLED` — leave unset or `false` until EC2 is ready; set to `true` to enable.
- `DEPLOY_PATH` — absolute application directory on EC2.
- `SYSTEMD_SERVICE` — systemd unit name to restart.
- `HEALTH_CHECK_URL` — public health endpoint URL.

The EC2 deploy user must be able to write `DEPLOY_PATH`, create/use its `.venv`, and run non-interactive `sudo systemctl restart` and `sudo systemctl is-active` for the configured service. The workflow excludes `.env` and virtual environments from the release archive, installs updated dependencies, restarts the service, and checks health. No deployment is attempted until the secrets and variables are configured.
