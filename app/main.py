from fastapi import FastAPI
from pydantic import BaseModel
import joblib, os

app = FastAPI()
VERSION = os.getenv("APP_VERSION", "v6")
model = joblib.load("app/model.joblib")          # loaded ONCE at startup, not per request
CLASSES = ["setosa", "versicolor", "virginica"]

class IrisFeatures(BaseModel):                    # request schema -> auto-validated
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

@app.get("/")
def root():
    return {"message": "hello from k8s", "version": VERSION}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(f: IrisFeatures):
    features = [[f.sepal_length, f.sepal_width, f.petal_length, f.petal_width]]
    pred = int(model.predict(features)[0])
    return {"class_id": pred, "class_name": CLASSES[pred]}