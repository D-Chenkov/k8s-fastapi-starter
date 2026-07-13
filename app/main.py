from fastapi import FastAPI
from pydantic import BaseModel
import joblib, os


MODEL_URI = os.getenv("MODEL_URI", "app/model.joblib")   # default: local file (CI-friendly)

def _load_model(uri):
    if uri.startswith("models:") or uri.startswith("runs:"):
        import mlflow.sklearn
        return mlflow.sklearn.load_model(uri)     # registry mode (real serving)
    return joblib.load(uri)                        # local file mode (CI / offline)

model = _load_model(MODEL_URI)

app = FastAPI()
VERSION = os.getenv("APP_VERSION", "v6")
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