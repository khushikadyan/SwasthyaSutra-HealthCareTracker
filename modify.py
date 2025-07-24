import pandas as pd
import numpy as np
# 1. Load your CSV file
file_path = 'dataset.csv'  # Change this to your actual file path/name
df = pd.read_csv(file_path)

# 2. Convert exercise minutes to days/week (60 minutes = 1 day)
df['exercise_days'] =np.clip(round(df['exercise_minutes'] / 60), 1,10).astype(int)

sleep_min, sleep_max = 4, 12
df['sleep_hours'] = np.clip(
    round((df['sleep_hours'] - sleep_min) / (sleep_max - sleep_min) * 9 + 1),
    1, 10
).astype(int)

df['diet_quality'] = np.clip(round(df['diet_quality']), 1, 10).astype(int)


# 3. Select only the columns you need
final_df = df[[
    'age',
    'gender',
    'height_cm',
    'weight_kg',
    'sleep_hours',
    'exercise_days',
    'stress_level',
    'diet_quality',
    'water_glasses'
]]

# 4. Save the cleaned data to a new CSV
output_file = 'health_data_clean.csv'
final_df.to_csv(output_file, index=False)

print(f"Data cleaned successfully! Saved to {output_file}")
print("\nFirst 5 rows of cleaned data:")
print(final_df.head())