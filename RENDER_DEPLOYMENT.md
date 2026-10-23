# Render deployment notes

This project publishes its tested container to GHCR through GitHub Actions.
Use the image:
ghcr.io/rushikeshavpeddi/student-result-prediction:latest

Render setup (requires signing in to your Render account):
1. Create > Web Service > Existing Image.
2. Enter the image above. If GHCR is private, add a registry credential with read:packages only.
3. Set the service port/environment variable PORT=8000.
4. Set health check path to /health.
5. Deploy, then verify /, /health, /docs, and POST /predict.

The Render service URL and deployment result can only be confirmed after the service is created in your Render account.
Do not commit registry tokens or credentials to this repository.
