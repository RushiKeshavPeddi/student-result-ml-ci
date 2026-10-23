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

    def test_high_performance_prediction(self):
        response = self.client.post("/predict", json={
            "attendance": 90, "internal_marks": 85,
            "assignment_marks": 88, "previous_score": 80
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["prediction"], "PASS")

    def test_missing_field_validation(self):
        response = self.client.post("/predict", json={"attendance": 90})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
