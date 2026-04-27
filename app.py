import streamlit as st
import pandas as pd
import pickle
import numpy as np
from pathlib import Path

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="DelivX – Delivery Time Prediction",
    page_icon="🚚",
    layout="centered"
)

# --- LOAD MODEL ---
@st.cache_resource
def load_model():
    model_path = Path("model.pkl")
    features_path = Path("feature_columns.pkl")
    
    if not model_path.exists() or not features_path.exists():
        st.error("Model files not found! Please ensure 'model.pkl' and 'feature_columns.pkl' exist.")
        return None, None
        
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(features_path, "rb") as f:
        features = pickle.load(f)
    return model, features

model, feature_columns = load_model()

# --- UI HEADER ---
st.title("DelivX – Delivery Time Prediction")
st.markdown("Enter delivery details below to estimate the delivery time.")

# --- INPUT SECTION ---
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        distance = st.number_input("Distance (km)", min_value=0.0, step=0.1, value=5.0)
        prep_time = st.number_input("Preparation Time (minutes)", min_value=0, step=1, value=15)
        weather = st.selectbox("Weather", ["Clear", "Rainy", "Fog", "Windy", "Snowy"])
        traffic = st.selectbox("Traffic Level", ["Low", "Medium", "High"])
        
    with col2:
        time_of_day = st.selectbox("Time of Day", ["Morning", "Afternoon", "Evening", "Night"])
        vehicle = st.selectbox("Vehicle Type", ["Bike", "Scooter", "Car"])
        experience_lvl = st.selectbox("Rider Experience Level", ["Beginner", "Intermediate", "Experienced"])

# --- MAPPING EXPERIENCE ---
experience_map = {
    "Beginner": 1.5,
    "Intermediate": 4.0,
    "Experienced": 8.0
}
experience_yrs = experience_map[experience_lvl]

# --- PREDICTION LOGIC ---
if st.button("Predict Delivery Time", use_container_width=True):
    if model is not None and feature_columns is not None:
        # Prepare input dataframe matching training format
        input_data = pd.DataFrame([{
            "Distance_km": distance,
            "Preparation_Time_min": prep_time,
            "Courier_Experience_yrs": experience_yrs,
            "Weather": weather,
            "Traffic_Level": traffic,
            "Time_of_Day": time_of_day,
            "Vehicle_Type": vehicle
        }])
        
        # Encoding categoricals (match training logic)
        input_encoded = pd.get_dummies(input_data)
        
        # Align with model feature columns
        input_aligned = input_encoded.reindex(columns=feature_columns, fill_value=0)
        
        # Predict
        try:
            prediction = model.predict(input_aligned)[0]
            
            st.divider()
            st.metric(label="Estimated Delivery Time", value=f"{prediction:.1f} minutes")
            st.success(f"Successfully calculated! The delivery is expected in approximately {prediction:.1f} minutes.")
        except Exception as e:
            st.error(f"Prediction failed: {e}")
    else:
        st.warning("Model is not loaded. Cannot predict.")

# --- FOOTER ---
st.markdown("---")
st.caption("Powered by DelivX ML Engine")
