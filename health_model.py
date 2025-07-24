import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

class HealthModel:
    def __init__(self):
        self.model = None
        self.model_path = 'health_model.joblib'
        self.initialize_model()

    def create_dummy_dataset(self):
        np.random.seed(42)
        num_samples = 1000
        
        data = {
            'age': np.random.randint(18, 80, num_samples),
            'gender': np.random.choice(['male', 'female', 'other'], num_samples),
            'weight_kg': np.random.uniform(45, 120, num_samples).round(1),
            'height_cm': np.random.uniform(150, 200, num_samples).round(1),
            'sleep_hours': np.random.uniform(4, 10, num_samples).round(1),
            'water_glasses': np.random.randint(2, 12, num_samples),
            'diet_quality': np.random.randint(1, 11, num_samples),
            'exercise_days': np.random.randint(0, 7, num_samples),
            'stress_level': np.random.randint(1, 11, num_samples)
        }
        
        data['bmi'] = data['weight_kg'] / ((data['height_cm']/100) ** 2)
        
        data['health_score'] = (
            0.3 * (10 - np.clip(data['stress_level'], 1, 10)) * 10 +
            0.2 * (data['sleep_hours'] / 8 * 10) +
            0.15 * (data['exercise_days'] / 7 * 10) +
            0.15 * (data['diet_quality'] / 10 * 10) +
            0.1 * (data['water_glasses'] / 8 * 10) +
            0.1 * (np.clip(25 / data['bmi'], 0.5, 1.5) * 10)
        ).round(1)
        
        data['health_score'] = np.clip(data['health_score'], 0, 100)
        
        return pd.DataFrame(data)

    def train_model(self):
        df = self.create_dummy_dataset()
        X = df.drop(['health_score', 'bmi'], axis=1)
        X = pd.get_dummies(X, columns=['gender'], drop_first=True)
        y = df['health_score']
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        joblib.dump(self.model, self.model_path)
        return self.model

    def load_model(self):
        return joblib.load(self.model_path)

    def initialize_model(self):
        if os.path.exists(self.model_path):
            self.model = self.load_model()
        else:
            self.model = self.train_model()

    def predict_health(self, input_data):
        df = pd.DataFrame([input_data])
        df = pd.get_dummies(df, columns=['gender'], drop_first=True)
        
        expected_cols = ['age', 'weight_kg', 'height_cm', 'sleep_hours', 'water_glasses', 
                        'diet_quality', 'exercise_days', 'stress_level', 'gender_male', 'gender_other']
        
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0
        
        df = df[expected_cols]
        return float(self.model.predict(df)[0])

    @staticmethod
    def calculate_bmi_category(bmi):
        if bmi < 18.5:
            return 'Underweight'
        elif 18.5 <= bmi < 25:
            return 'Normal'
        elif 25 <= bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

    @staticmethod
    def get_health_status(score):
        if score >= 80:
            return 'Excellent'
        elif 70 <= score < 80:
            return 'Good'
        elif 50 <= score < 70:
            return 'Fair'
        else:
            return 'Poor'