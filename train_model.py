import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

X, y = load_iris(return_X_y=True)
model = RandomForestClassifier(n_estimators=50, max_depth=3, random_state=42).fit(X, y)
joblib.dump(model, "app/model.joblib")   # save INTO app/ so the Dockerfile copies it
print("saved app/model.joblib")  