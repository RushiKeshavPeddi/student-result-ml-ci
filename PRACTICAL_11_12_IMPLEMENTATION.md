# Practical 11 and 12 — Implementation Notes

These experiments extend the existing Student Result Prediction project without retraining or changing its feature schema.

## Practical 11 — Logging and error tracking

The deployed FastAPI entry point is `api.py` (the Dockerfile starts `uvicorn api:app`). It now:

- Writes timestamped INFO/WARNING/ERROR records to standard output.
- Logs model loading and fails visibly if the model artifact cannot be loaded.
- Adds or preserves `X-Request-ID` and returns it in the response header.
- Logs HTTP method, route, status code, request ID, and elapsed milliseconds.
- Logs validation error locations/count without recording request bodies.
- Logs prediction success/failure without dumping the student's raw input values.

## Practical 12 — Metrics and monitoring

The same FastAPI application now exposes `/metrics` with these metric families:

- `student_api_http_requests_total`: HTTP request counter labelled by method, path, and status.
- `student_api_http_request_duration_seconds`: request duration histogram.
- `student_api_predictions_total`: prediction attempts labelled by success/error.
- `student_api_model_loaded`: model readiness gauge.

The `/metrics` scrape itself is excluded from user-traffic request metrics. Prometheus scrape configuration and alert rules are in `Practical_12_Monitoring/`.

## Validation

GitHub Actions installs dependencies, trains the existing project model as part of the established CI process, runs unit tests, builds the container, and checks `/health`, `/predict`, and `/metrics` before publishing the image to GHCR.

## Deployment steps still required in Render

After the GitHub Actions publish workflow succeeds:

1. Open the existing Render image-backed service.
2. Trigger a manual deploy of the latest image (or the new image revision).
3. Confirm the service is Live.
4. Test `/health`, `/docs`, and `/metrics` on the public URL.
5. Replace the placeholder hostname in `Practical_12_Monitoring/prometheus.yml` before running local Prometheus.

Prometheus and Grafana run locally with Docker. They are not hosted by the Render API service.
