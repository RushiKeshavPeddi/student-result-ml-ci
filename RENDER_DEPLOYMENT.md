# Render deployment notes

This project publishes its tested container to GHCR through GitHub Actions.

Image:
`ghcr.io/rushikeshavpeddi/student-result-prediction:latest`

## Initial deployment

1. In Render, choose **New → Web Service → Existing Image**.
2. Enter the image above. It is public, so registry credentials should not be needed.
3. The Docker image starts Uvicorn on `0.0.0.0:8000`.
4. Set health check path to `/health`.
5. Deploy and verify `/`, `/health`, `/docs`, and `POST /predict`.

## Redeploy after Practical 11 and Practical 12 changes

1. Open **GitHub → Actions** and wait for the latest **Practical 9 - Build, Test and Publish Student Result Prediction** run to succeed.
2. Confirm the workflow has passed unit tests, Docker build, health check, metrics check, and prediction check, then pushed the updated `latest` image to GHCR.
3. Open the existing Render service and choose **Manual Deploy → Deploy latest image** (wording may vary).
4. Wait for the deployment status to return to **Live**.
5. Verify:
   - `https://YOUR-RENDER-HOST.onrender.com/health`
   - `https://YOUR-RENDER-HOST.onrender.com/docs`
   - `https://YOUR-RENDER-HOST.onrender.com/metrics`
6. The metrics response should include `student_api_model_loaded 1.0`, `student_api_http_requests_total`, and `student_api_http_request_duration_seconds`.

## Prometheus and Grafana

Follow `Practical_12_Monitoring/README.md`. Replace the placeholder hostname in `prometheus.yml` with your Render hostname only (without `https://` or a path), then start Prometheus and Grafana using Docker.

The Render service URL and deployment result can only be confirmed after checking your Render account. Do not commit registry tokens or credentials to this repository.
