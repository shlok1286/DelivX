"""
DelivX – Model Training Script
Run once to generate:
  - model.pkl
  - feature_columns.pkl
"""

import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# ── 1. Load ────────────────────────────────────────────────────────────────
print("Loading dataset...")
df = pd.read_csv("Food_Delivery_Times.csv")
print(f"  Shape: {df.shape}")

# ── 2. Drop non-feature column ─────────────────────────────────────────────
df.drop(columns=["Order_ID"], inplace=True)

# ── 3. Handle missing values ───────────────────────────────────────────────
cat_cols = ["Weather", "Traffic_Level", "Time_of_Day", "Vehicle_Type"]
for col in cat_cols:
    df[col] = df[col].fillna(df[col].mode()[0])

df["Courier_Experience_yrs"] = df["Courier_Experience_yrs"].fillna(df["Courier_Experience_yrs"].median())
print(f"  Missing after imputation: {df.isnull().sum().sum()}")

# ── 4. Features / Target ───────────────────────────────────────────────────
X = df.drop("Delivery_Time_min", axis=1)
y = df["Delivery_Time_min"]

# ── 5. Encode categoricals ─────────────────────────────────────────────────
X = pd.get_dummies(X, drop_first=True)
feature_columns = list(X.columns)
print(f"  Features after encoding: {len(feature_columns)}")

# ── 6. Train / Test split ──────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── 7. Train ───────────────────────────────────────────────────────────────
print("Training RandomForestRegressor (200 trees)...")
model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# ── 8. Evaluate ────────────────────────────────────────────────────────────
preds = model.predict(X_test)
mae   = mean_absolute_error(y_test, preds)
r2    = r2_score(y_test, preds)
print(f"\n  ✅  MAE : {mae:.2f} minutes")
print(f"  ✅  R²  : {r2:.4f}")

# ── 9. Save ────────────────────────────────────────────────────────────────
pickle.dump(model,           open("model.pkl",           "wb"))
pickle.dump(feature_columns, open("feature_columns.pkl", "wb"))
print("\n  💾  Saved model.pkl and feature_columns.pkl")
print("\nDone! Run `python app.py` to start the web server.")
