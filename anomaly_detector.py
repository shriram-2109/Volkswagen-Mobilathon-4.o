import joblib
import pandas as pd
from typing import Tuple

class AnomalyDetector:
    def __init__(self, model_path: str, scaler_path: str):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
    
    def detect(self, data: pd.DataFrame) -> Tuple[bool, float]:
        scaled_data = self.scaler.transform(data)
        anomaly_score = -self.model.decision_function(scaled_data)
        anomaly = self.model.predict(scaled_data) == -1
        return anomaly, anomaly_score