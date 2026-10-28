import unittest
from fastapi.testclient import TestClient
from api import app


class TestFastAPIPredictionApplication(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_swagger_docs_endpoint(self):
        response = self.client.get("/docs")
        self.assertEqual(response.status_code, 200)

    def test_metrics_endpoint_exposes_application_metrics(self):
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("student_api_model_loaded", response.text)
        self.assertIn("student_api_http_requests_total", response.text)
        self.assertIn("student_api_http_request_duration_seconds", response.text)

    def test_request_id_is_returned(self):
        response = self.client.get("/health", headers={"X-Request-ID": "practical-test-123"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-Request-ID"), "practical-test-123")

    def test_high_performance_prediction(self):
        response = self.client.post("/predict", json={
            "attendance": 90, "internal_marks": 85,
            "assignment_marks": 88, "previous_score": 80
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["prediction"], "PASS")
        self.assertIn("X-Request-ID", response.headers)

    def test_missing_field_validation_is_tracked(self):
        response = self.client.post("/predict", json={"attendance": 90})
        self.assertEqual(response.status_code, 422)
        self.assertIn("X-Request-ID", response.headers)


if __name__ == "__main__":
    unittest.main()
