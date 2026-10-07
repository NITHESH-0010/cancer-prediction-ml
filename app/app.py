import os
import math
import traceback
import joblib
import numpy as np
from flask import Flask, render_template, request, jsonify
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, '..', 'models')
model_path = os.path.join(MODELS_DIR, 'best_cancer_model.pkl')
scaler_path = os.path.join(MODELS_DIR, 'scaler.pkl')
metrics_path = os.path.join(MODELS_DIR, 'metrics.json')

if not os.path.exists(model_path) or not os.path.exists(scaler_path):
    print(f"Startup failed: Missing model or scaler in {MODELS_DIR}")
    exit(1)

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

try:
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
except:
    metrics = {"cv_accuracy": 0.0, "cv_auc": 0.0}

app = Flask(__name__)

# Age, BMI, Smoking, GeneticRisk, PhysicalActivity, AlcoholIntake, CancerHistory
MEDIAN_PATIENT = np.array([[51.0, 27.598494, 0.0, 0.0, 4.834316, 2.382971, 0.0]])
FEATURE_NAMES = ["Age", "BMI", "Smoking", "GeneticRisk", "PhysicalActivity", "AlcoholIntake", "CancerHistory"]

TIPS = {
    "Age": ("Advancing age increases baseline risk.", "Stay up to date with age-appropriate screenings."),
    "BMI": ("Higher BMI is linked to inflammation and altered hormones.", "Aim for a balanced diet and regular exercise to maintain a healthy weight."),
    "Smoking": ("Smoking damages DNA and introduces carcinogens.", "Consider smoking cessation programs or nicotine replacement."),
    "GeneticRisk": ("Inherited markers elevate susceptibility.", "Discuss genetic counseling or earlier screening with your doctor."),
    "PhysicalActivity": ("Low activity levels can impact metabolism and immune function.", "Try to incorporate at least 150 minutes of moderate activity per week."),
    "AlcoholIntake": ("Excessive alcohol can damage tissues and affect liver function.", "Limit alcohol consumption to recommended guidelines."),
    "CancerHistory": ("Personal or family history indicates higher predisposition.", "Ensure strict adherence to follow-up surveillance.")
}

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/')
def home():
    return render_template('index.html', result=None, metrics=metrics)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        inputs = []
        for feat in FEATURE_NAMES:
            if feat not in request.form or request.form[feat].strip() == '':
                return f"Missing value for {feat}", 400
            try:
                val = float(request.form[feat])
            except ValueError:
                return f"Invalid numeric value for {feat}", 400
            if not math.isfinite(val):
                return f"Invalid value (NaN/Inf) for {feat}", 400
            inputs.append(val)
        
        gender_val = request.form.get('Gender', '')
        if gender_val == '1': gender_str = 'Male'
        elif gender_val == '0': gender_str = 'Female'
        else: gender_str = 'Prefer not to say'
        
        age, bmi, smoking, genetic_risk, physical_activity, alcohol_intake, cancer_history = inputs
        
        if not (1 <= age <= 120): return "Age must be between 1 and 120", 400
        if not (10 <= bmi <= 70): return "BMI must be between 10 and 70", 400
        if not (0 <= physical_activity <= 40): return "Physical Activity must be between 0 and 40", 400
        if not (0 <= alcohol_intake <= 50): return "Alcohol Intake must be between 0 and 50", 400
        if smoking not in {0.0, 1.0}: return "Smoking must be 0 or 1", 400
        if genetic_risk not in {0.0, 1.0, 2.0}: return "GeneticRisk must be 0, 1, or 2", 400
        if cancer_history not in {0.0, 1.0}: return "CancerHistory must be 0 or 1", 400

        user_input = np.array([inputs])
        base_prob = model.predict_proba(scaler.transform(MEDIAN_PATIENT))[0][1]
        final_prob = model.predict_proba(scaler.transform(user_input))[0][1]
        final_prob = min(final_prob, 0.999)
        
        effects = []
        for i in range(7):
            occluded = user_input.copy()
            occluded[0, i] = MEDIAN_PATIENT[0, i]
            prob_occ = model.predict_proba(scaler.transform(occluded))[0][1]
            effects.append(final_prob - prob_occ)
            
        sum_effects = sum(effects)
        diff = final_prob - base_prob
        scaled_effects = []
        for e in effects:
            if abs(sum_effects) > 1e-6:
                scaled_effects.append(e * (diff / sum_effects))
            else:
                scaled_effects.append(diff / 7.0)
                
        factors = []
        for i, feat in enumerate(FEATURE_NAMES):
            factors.append({
                "name": feat,
                "effect": scaled_effects[i] * 100
            })
            
        factors.sort(key=lambda x: x["effect"], reverse=True)
        top_factors = [f for f in factors if f["effect"] > 0][:3]
        tips = []
        for f in top_factors:
            cause, tip = TIPS[f["name"]]
            tips.append({"name": f["name"], "cause": cause, "tip": tip})

        risk_pct = final_prob * 100
        if risk_pct < 30: risk_band = "Low"
        elif risk_pct < 60: risk_band = "Moderate"
        else: risk_band = "High"

        if bmi < 18.5: bmi_status = "Underweight"
        elif bmi < 25: bmi_status = "Normal Weight"
        elif bmi < 30: bmi_status = "Overweight"
        else: bmi_status = "Obese"

        result = {
            "risk_pct": risk_pct,
            "risk_band": risk_band,
            "factors": factors,
            "tips": tips,
            "bmi_status": bmi_status,
            "gender_str": gender_str,
            "age": age, "bmi": bmi, "smoking": smoking,
            "genetic_risk": genetic_risk, "physical_activity": physical_activity,
            "alcohol_intake": alcohol_intake, "cancer_history": cancer_history
        }

        return render_template('index.html', result=result, metrics=metrics)

    except Exception as e:
        print(traceback.format_exc())
        return "An unexpected error occurred processing your request.", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)