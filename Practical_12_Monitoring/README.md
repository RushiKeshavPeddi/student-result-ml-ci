# Practical 12 — Prometheus and Grafana Monitoring

This folder provides the Prometheus scrape configuration and alert rules for the deployed Student Result Prediction API.

## Before starting

1. Deploy the updated image to Render after the Practical 11/12 GitHub Actions run succeeds.
2. Open `https://YOUR-RENDER-HOST.onrender.com/metrics` and confirm it returns Prometheus text including `student_api_model_loaded 1.0`.
3. Replace `REPLACE_WITH_YOUR_RENDER_HOST.onrender.com` in `prometheus.yml` with the hostname only. Do not include `https://` or a path.

## Run Prometheus on Windows PowerShell

Open PowerShell in this folder. Ensure Docker Desktop is running.

```powershell
docker network create mlops-monitoring
```

If the network already exists, continue. Start Prometheus:

```powershell
docker run -d --name prometheus --network mlops-monitoring -p 9090:9090 -v "${PWD}/prometheus.yml:/etc/prometheus/prometheus.yml:ro" -v "${PWD}/student_api_alerts.yml:/etc/prometheus/student_api_alerts.yml:ro" prom/prometheus
```

Open [Prometheus Targets](http://localhost:9090/targets). The `student-result-api` target should become **UP**.

## Useful PromQL queries

Run these individually at [Prometheus](http://localhost:9090):

```promql
student_api_model_loaded
sum(student_api_http_requests_total)
sum(rate(student_api_http_requests_total[1m]))
sum(student_api_predictions_total{result="success"})
sum(rate(student_api_http_requests_total{status=~"4..|5.."}[5m]))
histogram_quantile(0.95, sum by (le) (rate(student_api_http_request_duration_seconds_bucket[5m])))
up{job="student-result-api"}
```

## Run Grafana

```powershell
docker run -d --name grafana --network mlops-monitoring -p 3000:3000 grafana/grafana
```

Open [Grafana](http://localhost:3000). Add a Prometheus data source with URL `http://prometheus:9090`, then create a dashboard with panels for model readiness, total requests, request rate, successful predictions, error rate, and P95 latency.

## Alert rules

The mounted `student_api_alerts.yml` defines a client-error alert and an API-down alert. View rule state at Prometheus **Alerts**. Prometheus evaluates alert rules; external email/chat notifications require separate Alertmanager or Grafana contact-point configuration.

## Cleanup

```powershell
docker rm -f grafana prometheus
```

Do not place tokens, passwords, or student-identifying information in this folder.
