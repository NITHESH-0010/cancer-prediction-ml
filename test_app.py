import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
import numpy as np
from app.app import app, FEATURE_NAMES, model

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_feature_order():
    expected = ["Age", "BMI", "Smoking", "GeneticRisk", "PhysicalActivity", "AlcoholIntake", "CancerHistory"]
    assert FEATURE_NAMES == expected
    assert model.n_features_in_ == 7

def test_valid_input(client):
    data = {
        "Age": "45",
        "BMI": "24.5",
        "Smoking": "0",
        "GeneticRisk": "1",
        "PhysicalActivity": "10",
        "AlcoholIntake": "5",
        "CancerHistory": "0"
    }
    rv = client.post('/predict', data=data)
    assert rv.status_code == 200

def test_missing_field(client):
    data = {
        "Age": "45",
        "BMI": "24.5",
        # Missing Smoking
        "GeneticRisk": "1",
        "PhysicalActivity": "10",
        "AlcoholIntake": "5",
        "CancerHistory": "0"
    }
    rv = client.post('/predict', data=data)
    assert rv.status_code == 400

def test_nan_input(client):
    data = {
        "Age": "45",
        "BMI": "NaN",
        "Smoking": "0",
        "GeneticRisk": "1",
        "PhysicalActivity": "10",
        "AlcoholIntake": "5",
        "CancerHistory": "0"
    }
    rv = client.post('/predict', data=data)
    assert rv.status_code == 400

def test_inf_input(client):
    data = {
        "Age": "45",
        "BMI": "24.5",
        "Smoking": "inf",
        "GeneticRisk": "1",
        "PhysicalActivity": "10",
        "AlcoholIntake": "5",
        "CancerHistory": "0"
    }
    rv = client.post('/predict', data=data)
    assert rv.status_code == 400

def test_out_of_range_age(client):
    data = {
        "Age": "150",
        "BMI": "24.5",
        "Smoking": "0",
        "GeneticRisk": "1",
        "PhysicalActivity": "10",
        "AlcoholIntake": "5",
        "CancerHistory": "0"
    }
    rv = client.post('/predict', data=data)
    assert rv.status_code == 400

def test_invalid_category(client):
    data = {
        "Age": "45",
        "BMI": "24.5",
        "Smoking": "0",
        "GeneticRisk": "3",  # invalid
        "PhysicalActivity": "10",
        "AlcoholIntake": "5",
        "CancerHistory": "0"
    }
    rv = client.post('/predict', data=data)
    assert rv.status_code == 400

def test_gender_invariance(client):
    data1 = {
        "Age": "45", "BMI": "24.5", "Smoking": "0", "GeneticRisk": "1", 
        "PhysicalActivity": "10", "AlcoholIntake": "5", "CancerHistory": "0",
        "Gender": "1"  # Male
    }
    data2 = data1.copy()
    data2["Gender"] = "0"  # Female
    
    rv1 = client.post('/predict', data=data1)
    rv2 = client.post('/predict', data=data2)
    
    assert rv1.status_code == 200
    assert rv2.status_code == 200
    
    import re
    def extract_risk(html):
        match = re.search(r'>\s*([0-9.]+)%</text>', html.decode('utf-8'))
        return match.group(1) if match else None

    def extract_factors(html):
        factors = re.findall(r'<div class="bar-label".*?>(.*?)</div>.*?<div class="bar-value">\s*([+-]?[0-9.]+\s*pts)\s*</div>', html.decode('utf-8'), re.DOTALL)
        return factors

    risk1 = extract_risk(rv1.data)
    risk2 = extract_risk(rv2.data)
    assert risk1 is not None and risk1 == risk2, f"Risk should be identical regardless of Gender. Got {risk1} and {risk2}"

    factors1 = extract_factors(rv1.data)
    factors2 = extract_factors(rv2.data)
    assert factors1 == factors2, "Factor contributions should be identical regardless of Gender"
    assert "Gender" not in FEATURE_NAMES
