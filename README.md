# Student Result Prediction — MLOps CI/CD

This repository demonstrates the Student Result Prediction project across Practicals 2–12: model training, automated tests, a model quality gate, release artifacts, prediction APIs, Docker validation, GHCR publication, Render deployment, logging, metrics, and monitoring configuration.

## Project files

- `train_model.py` — creates a deterministic student dataset, trains a Logistic Regression pipeline, and writes the model and metrics.
- `quality_gate.py` — requires model accuracy of at least 0.85.
- `test_ml_pipeline.py` — tests generated data, model, metrics, and predictions.
- `app.py` — Flask prediction API used for the earlier Continuous Delivery practical.
- `test_app.py` — Flask API tests.
- `api.py` — FastAPI service used for Docker, GHCR, and cloud deployment; includes Practical 11 logging and Practical 12 Prometheus metrics.
- `test_api.py` — FastAPI health, docs, prediction, request ID, validation, and metrics tests.
- `Dockerfile` and `.dockerignore` — container build configuration.
- `.github/workflows/ml-ci.yml` — trains, gates, tests, Docker-validates, and uploads release artifacts.
- `.github/workflows/ghcr-manual-publish.yml` — manually triggered, tested-image GHCR publishing workflow for Practical 8.
- `.github/workflows/docker-publish.yml` — automatically builds, tests, and publishes the container to GHCR for Practical 9.
- `RENDER_DEPLOYMENT.md` — steps to deploy the published image from GHCR to Render.
- `PRACTICAL_11_12_IMPLEMENTATION.md` — summary of both observability experiments and the remaining deployment steps.
- `Practical_12_Monitoring/prometheus.yml` — Prometheus scrape configuration; replace the placeholder with your Render hostname.
- `Practical_12_Monitoring/student_api_alerts.yml` — classroom client-error and service-down alert rules.
- `Practical_12_Monitoring/README.md` — Windows/Docker instructions for Prometheus and Grafana.

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
- `GET /metrics` — Prometheus metrics; does not count its own scrape requests as user traffic.

Example request body is available in `test_payload.json`.

## Practical 11 — Logging and error tracking

Logs are written to standard output and include model-loading events, request IDs, HTTP method/path/status, response duration, validation-error locations/count, and prediction success/failure. Raw request bodies and secrets are not logged. Responses include an `X-Request-ID` header.

## Practical 12 — Prometheus and Grafana

The API exposes:

- `student_api_http_requests_total` — HTTP request counter.
- `student_api_http_request_duration_seconds` — response-time histogram.
- `student_api_predictions_total` — inference success/error counter.
- `student_api_model_loaded` — model-loaded gauge.

See `Practical_12_Monitoring/README.md` for Docker commands, PromQL examples, Grafana data-source setup, dashboard panels, and alert verification.

## GitHub Actions and GHCR

The CI workflow trains the model, checks the 0.85 accuracy threshold, runs tests, builds the Docker image, checks `/health`, `/predict`, and `/metrics`, and uploads release artifacts.

The Practical 8 workflow can be started from **Actions → Practical 8 - Publish Tested Image to GHCR → Run workflow**. The Practical 9 workflow runs on pushes to `main`, tests the image before publication, and publishes `v1`, `latest`, and commit-specific `sha-<commit>` tags to:

`ghcr.io/rushikeshavpeddi/student-result-prediction`

## Render deployment

Render account setup is performed in the Render Dashboard. Follow `RENDER_DEPLOYMENT.md`, use the tested GHCR image, configure the port/health check to match the service, then verify `/`, `/health`, `/docs`, and `/predict`. After Practical 11/12 changes publish successfully, manually redeploy the updated `latest` image on Render and verify `/metrics` as well. Never commit registry tokens or other credentials.
