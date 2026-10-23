from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Student Result Prediction API",
    description="Predict a student's result from attendance and assessment marks.",
    version="1.0.0",
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
        raise HTTPException(status_code=503, detail="Model is not available; run training first.")
    return joblib.load(MODEL_PATH)


@app.get("/")
def root():
    return {"status": "ok", "service": "student-result-prediction", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "student-result-prediction"}


@app.post("/predict")
def predict(student: StudentInput):
    sample = pd.DataFrame([student.model_dump()])
    prediction_code = int(load_model().predict(sample)[0])
    return {
        "prediction": "PASS" if prediction_code == 1 else "FAIL",
        "prediction_code": prediction_code,
    }
