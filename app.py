"""
DeliverIQ – Flask Web Application
"""

from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd

app = Flask(__name__)

# ── Load saved artefacts ───────────────────────────────────────────────────
model           = pickle.load(open("model.pkl", "rb"))
feature_columns = pickle.load(open("feature_columns.pkl", "rb"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        distance    = float(data["distance"])
        weather     = data["weather"]
        traffic     = data["traffic"]
        time_of_day = data["time_of_day"]
        vehicle     = data["vehicle"]
        prep_time   = float(data["prep_time"])
        experience  = float(data["experience"])

        # Build single-row DataFrame matching training schema
        row = pd.DataFrame([{
            "Distance_km":            distance,
            "Weather":                weather,
            "Traffic_Level":          traffic,
            "Time_of_Day":            time_of_day,
            "Vehicle_Type":           vehicle,
            "Preparation_Time_min":   prep_time,
            "Courier_Experience_yrs": experience,
        }])

        row_encoded = pd.get_dummies(row)
        row_aligned = row_encoded.reindex(columns=feature_columns, fill_value=0)

        prediction = model.predict(row_aligned)[0]

        return jsonify({"success": True, "prediction": round(float(prediction), 1)})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
