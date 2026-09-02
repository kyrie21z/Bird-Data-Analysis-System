# Repository Guidelines

## Project Structure & Module Organization

The Flask backend lives in `backend/`. `backend/app/api/main.py` defines HTTP routes, `models.py` contains SQLAlchemy models, and `app/utils/` holds caching, error handling, and PDF reporting helpers. Static Bootstrap/Leaflet/ECharts pages are in `frontend/`; keep page-specific markup, styles, and scripts with the relevant HTML unless code is shared. Database definitions are in `database/init.sql` and `schema.sql`. Sample bird images and audio are under `data/`, while user and deployment documentation belongs in `docs/`.

## Build, Test, and Development Commands

Use the project's Conda environment and install dependencies:

```bash
conda activate bird-analysis
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
```

Install any additional development or test packages needed for your task into `bird-analysis`, and record persistent runtime dependencies in `backend/requirements.txt`.

Run `cd backend && python run_dev.py` to start the Flask API and bundled frontend at `http://localhost:5000`. For a MySQL setup, initialize tables with `mysql -u root -p < database/init.sql`. Use `python -m compileall backend` as a quick syntax check. Smoke-test a running service with `curl http://localhost:5000/api/stats`.

## Coding Style & Naming Conventions

Use four-space indentation in Python, follow PEP 8, and preserve the existing UTF-8 Chinese docstrings and user-facing text. Name functions and variables `snake_case`, model classes `PascalCase`, and constants `UPPER_SNAKE_CASE`. Keep routes thin: database behavior belongs in models and reusable cross-cutting logic in `app/utils/`. HTML, CSS, and JavaScript also use four-space indentation. No formatter or linter is configured, so match nearby code and avoid unrelated reformatting.

## Testing Guidelines

There is currently no automated test suite or coverage threshold. Every change should pass `compileall` and receive a focused API or browser smoke test. When adding tests, place them in `tests/`, name files `test_*.py`, use Flask's test client with the `testing` configuration, and document any new test dependency and command in the same pull request.

## Commit & Pull Request Guidelines

Recent feature commits use Conventional Commit-style subjects such as `feat(api): ...` and `feat(report): ...`; follow `type(scope): concise description` where practical. Keep each commit focused. Pull requests should explain the behavior change, list verification performed, link related issues, and call out schema or configuration changes. Include screenshots for frontend changes and representative request/response examples for API changes.

## Security & Configuration

Use `backend/.env.example` as the configuration template. Keep real secrets, local `.env` files, SQLite databases, and logs out of commits. Replace the development `SECRET_KEY` and database credentials in deployed environments.
