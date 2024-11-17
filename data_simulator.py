import numpy as np
import pandas as pd

class DataSimulator:
    @staticmethod
    def generate_data():
        return pd.DataFrame([{
            'machine_temp': np.random.normal(70, 10),
            'power_consumption': np.random.normal(8, 1.5),
            'vibration': np.random.normal(1, 0.5),
            'pressure': np.random.normal(25, 5),
            'production_rate': np.random.normal(90, 10),
            'cycle_time': np.random.normal(35, 5),
            'lubricant_level': np.random.uniform(50, 100)
        }])