# Student Result Prediction — MLOps CI/CD

This repository demonstrates the Student Result Prediction project across Practicals 2–10: model training, automated tests, a model quality gate, release artifacts, prediction APIs, Docker validation, GHCR publication, and preparation for Render deployment.

## Project files

- `train_model.py` — creates a deterministic student dataset, trains a Logistic Regression pipeline, and writes the model and metrics.
- `quality_gate.py` — requires model accuracy of at least 0.85.
- `test_ml_pipeline.py` — tests generated data, model, metrics, and predictions.
- `app.py` — Flask prediction API used for the Continuous Delivery practical.
- `test_app.py` — Flask API tests.
- `api.py` — FastAPI service used for Docker, GHCR, and cloud deployment practicals.
- `test_api.py` — FastAPI health, docs, and prediction tests.
- `Dockerfile` and `.dockerignore` — container build configuration.
- `.github/workflows/ml-ci.yml` — trains, gates, tests, Docker-validates, and uploads release artifacts.
- `.github/workflows/ghcr-manual-publish.yml` — manually triggered, tested-image GHCR publishing workflow for Practical 8.
- `.github/workflows/docker-publish.yml` — automatically builds, tests, and publishes the container to GHCR for Practical 9.
- `RENDER_DEPLOYMENT.md` — steps to deploy the published image from GHCR to Render.

## Local setup

Use Python 3.11 or later.

```bash
python -m pip install -r requirements.txt
python train_model.py
python quality_gate.py
python -m unittest discover -v
```

The training script generates `student_result_model.pkl`, `metrics.json`, and `student_results.csv`. These are generated workflow outputs and do not need to be committed.

## API endpoints

The Docker image runs the FastAPI service on port 8000:

- `GET /` — service status.
- `GET /health` — health check.
- `GET /docs` — interactive Swagger UI.
- `POST /predict` — accepts JSON with `attendance`, `internal_marks`, `assignment_marks`, and `previous_score`.

Example request body is available in `test_payload.json`.

## GitHub Actions and GHCR

The CI workflow trains the model, checks the 0.85 accuracy threshold, runs tests, builds the Docker image, checks the live container, and uploads the `student-result-ml-release` and `student-result-ml-artifacts` artifacts.

The Practical 8 workflow can be started from **Actions → Practical 8 - Publish Tested Image to GHCR → Run workflow**. The Practical 9 workflow runs on pushes to `main`, tests the image before publication, and publishes `v1`, `latest`, and commit-specific `sha-<commit>` tags to:

`ghcr.io/rushikeshavpeddi/student-result-prediction`

## Render deployment

Render account setup is performed in the Render Dashboard. Follow `RENDER_DEPLOYMENT.md`, use the tested GHCR image, configure port `8000` and health path `/health`, then verify `/`, `/health`, `/docs`, and `/predict`. Never commit registry tokens or other credentials.
