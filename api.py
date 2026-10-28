from pathlib import Path
import logging
import sys
import time
import uuid

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger("student-result-api")

HTTP_REQUESTS = Counter(
    "student_api_http_requests_total",
    "Total HTTP requests received by the Student Result Prediction API",
    ["method", "path", "status"],
)
HTTP_LATENCY = Histogram(
    "student_api_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)
PREDICTIONS = Counter(
    "student_api_predictions_total",
    "Total Student Result Prediction inference attempts",
    ["result"],
)
MODEL_LOADED = Gauge(
    "student_api_model_loaded",
    "Whether the trained Student Result Prediction model loaded successfully",
)

app = FastAPI(
    title="Student Result Prediction API",
    description="Predict a student's result from attendance and assessment marks.",
    version="1.1.0",
)
MODEL_PATH = Path("student_result_model.pkl")
FEATURES = ["attendance", "internal_marks", "assignment_marks", "previous_score"]


class StudentInput(BaseModel):
    attendance: float = Field(ge=0, le=100)
    internal_marks: float = Field(ge=0, le=100)
    assignment_marks: float = Field(ge=0, le=100)
    previous_score: float = Field(ge=0, le=100)


def load_model():
    if not MODEL_PATH.exists():
        MODEL_LOADED.set(0)
        logger.error("event=model_load_failed reason=model_file_missing model_file=%s", MODEL_PATH)
        raise RuntimeError("Trained model file is missing.")
    try:
        loaded_model = joblib.load(MODEL_PATH)
        MODEL_LOADED.set(1)
        logger.info("event=model_loaded model_file=%s", MODEL_PATH.name)
        return loaded_model
    except Exception:
        MODEL_LOADED.set(0)
        logger.exception("event=model_load_failed model_file=%s", MODEL_PATH.name)
        raise


try:
    model = load_model()
except Exception:
    # Keep startup failure visible and fail fast rather than serving an API that cannot predict.
    raise


@app.middleware("http")
async def request_logging_and_metrics_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    method = request.method
    path = request.url.path
    started = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration = time.perf_counter() - started
        logger.exception(
            "event=http_request_exception request_id=%s method=%s path=%s duration_ms=%.2f",
            request_id, method, path, duration * 1000,
        )
        raise

    duration = time.perf_counter() - started
    status = response.status_code
    response.headers["X-Request-ID"] = request_id

    # Do not count Prometheus scrapes as user traffic.
    if path != "/metrics":
        HTTP_REQUESTS.labels(method=method, path=path, status=str(status)).inc()
        HTTP_LATENCY.labels(method=method, path=path).observe(duration)

    level_logger = logger.warning if status >= 400 else logger.info
    level_logger(
        "event=http_request request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
        request_id, method, path, status, duration * 1000,
    )
    return response


@app.exception_handler(RequestValidationError)
async def log_validation_error(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    field_locations = [list(error.get("loc", ())) for error in errors]
    logger.warning(
        "event=validation_error request_id=%s path=%s field_locations=%s error_count=%s",
        getattr(request.state, "request_id", "unknown"),
        request.url.path,
        field_locations,
        len(errors),
    )
    return await request_validation_exception_handler(request, exc)


@app.get("/")
def root():
    return {"status": "ok", "service": "student-result-prediction", "version": "1.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "student-result-prediction"}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict")
def predict(student: StudentInput, request: Request):
    payload = student.model_dump()
    logger.info(
        "event=prediction_request request_id=%s feature_names=%s",
        getattr(request.state, "request_id", "unknown"),
        sorted(payload.keys()),
    )
    try:
        sample = pd.DataFrame([payload], columns=FEATURES)
        prediction_code = int(model.predict(sample)[0])
        PREDICTIONS.labels(result="success").inc()
        logger.info(
            "event=prediction_success request_id=%s prediction=%s",
            getattr(request.state, "request_id", "unknown"),
            "PASS" if prediction_code == 1 else "FAIL",
        )
        return {
            "prediction": "PASS" if prediction_code == 1 else "FAIL",
            "prediction_code": prediction_code,
        }
    except Exception as exc:
        PREDICTIONS.labels(result="error").inc()
        logger.exception(
            "event=prediction_failed request_id=%s",
            getattr(request.state, "request_id", "unknown"),
        )
        raise HTTPException(status_code=500, detail="Prediction failed") from exc
