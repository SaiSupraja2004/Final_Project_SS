from flask import Flask, render_template, request, jsonify
import requests
import joblib
import numpy as np
import os
from transformers import pipeline

app = Flask(__name__)

# ==============================
# 🧠 Load ML Disease Prediction Model
# ==============================
model = joblib.load("model/disease_prediction_model.pkl")
symptom_list = joblib.load("model/symptom_list.pkl")

# ==============================
# 🤖 Load Local Precautions Generator
# ==============================
print("🧠 Loading local GPT model for precautions...")
precaution_model = pipeline(
    "text-generation",
    model="distilgpt2"
)
print("✅ GPT model loaded successfully!")

# ==============================
# 🌍 ROUTE: Find Hospitals by City
# ==============================
@app.route("/find-hospitals", methods=["GET"])
def find_hospitals():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City required"}), 400

    try:
        geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={city}"
        geo_res = requests.get(geo_url, headers={"User-Agent": "SymptoCare"}).json()
        if not geo_res:
            return jsonify({"results": []})

        lat = geo_res[0]["lat"]
        lon = geo_res[0]["lon"]

        overpass_url = (
            f"https://overpass-api.de/api/interpreter?"
            f"data=[out:json];node['amenity'='hospital'](around:5000,{lat},{lon});out;"
        )
        res = requests.get(overpass_url, headers={"User-Agent": "SymptoCare"}).json()

        hospitals = [
            {"name": n["tags"].get("name", "Unnamed Hospital"), "lat": n["lat"], "lon": n["lon"]}
            for n in res.get("elements", [])
        ]
        return jsonify({"results": hospitals})

    except Exception as e:
        print("❌ Hospital error:", e)
        return jsonify({"error": "Failed to fetch hospital data"}), 500


# ==============================
# 💊 ROUTE: Find Medical Shops by City
# ==============================
@app.route("/find-medicalshops", methods=["GET"])
def find_medicalshops():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City required"}), 400

    try:
        geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={city}"
        geo_res = requests.get(geo_url, headers={"User-Agent": "SymptoCare"}).json()
        if not geo_res:
            return jsonify({"results": []})

        lat = geo_res[0]["lat"]
        lon = geo_res[0]["lon"]

        overpass_url = (
            f"https://overpass-api.de/api/interpreter?"
            f"data=[out:json];node['amenity'='pharmacy'](around:5000,{lat},{lon});out;"
        )
        res = requests.get(overpass_url, headers={"User-Agent": "SymptoCare"}).json()

        shops = [
            {"name": n["tags"].get("name", "Unnamed Pharmacy"), "lat": n["lat"], "lon": n["lon"]}
            for n in res.get("elements", [])
        ]
        return jsonify({"results": shops})

    except Exception as e:
        print("❌ Medical shop error:", e)
        return jsonify({"error": "Failed to fetch medical shop data"}), 500


# ==============================
# 🧠 ROUTE: Precautions (Local AI Generator)
# ==============================
@app.route("/precautions", methods=["POST"])
def precautions():
    data = request.get_json()
    disease = data.get("disease", "").strip().lower()

    if not disease:
        return jsonify({"precautions": "Please enter a disease name."})

    try:
        prompt = (
            f"List four short and safe medical precautions for someone suffering from {disease}. "
            f"Write them as numbered points, each one clear and simple."
        )

        # Generate text locally using GPT-2
        output = precaution_model(
            prompt,
            max_length=120,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )

        text = output[0]["generated_text"]

        # Clean out the prompt part if it repeats
        advice = text.replace(prompt, "").strip()

        # Optional cleanup for GPT-2 quirks
        advice = advice.split("\n\n")[0].strip()

        return jsonify({"precautions": advice})

    except Exception as e:
        print("❌ Precautions generation error:", e)
        return jsonify({
            "precautions": "Failed to generate advice locally. Please consult a doctor."
        })


# ==============================
# 🩺 ROUTE: Disease Prediction
# ==============================
@app.route("/predict-disease", methods=["POST"])
def predict_disease():
    data = request.get_json()
    symptoms = data.get("symptoms", [])
    input_vector = [1 if s in symptoms else 0 for s in symptom_list]
    prediction = model.predict([input_vector])[0]
    return jsonify({"disease": prediction})


# ==============================
# 🌐 ROUTES: Page Rendering
# ==============================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict")
def predict_page():
    return render_template("predict.html")


@app.route("/hospitals")
def hospitals_page():
    return render_template("hospitals.html")


@app.route("/shops")
def shops_page():
    return render_template("shops.html")


@app.route("/precautions")
def precautions_page():
    return render_template("precautions.html")


# ==============================
# 🚀 Run the Flask App
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
