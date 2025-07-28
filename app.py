"""
Flask Crop Recommendation System
================================

A machine learning-powered web application that recommends optimal crops
based on soil and environmental conditions.

Author: Crop Recommendation System
Version: 2.0.0
"""

from flask import Flask, request, render_template, url_for
import numpy as np
import pickle
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
class Config:
    """Application configuration."""
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

app.config.from_object(Config)

# Crop mapping constants
CROP_DICT = {
    1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya",
    7: "Orange", 8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes",
    12: "Mango", 13: "Banana", 14: "Pomegranate", 15: "Lentil", 16: "Blackgram",
    17: "Mungbean", 18: "Mothbeans", 19: "Pigeonpeas", 20: "Kidneybeans",
    21: "Chickpea", 22: "Coffee"
}

CROP_ICONS = {
    1: "🌾", 2: "🌽", 3: "🌿", 4: "🌸", 5: "🥥", 6: "🧡",
    7: "🍊", 8: "🍎", 9: "🍈", 10: "🍉", 11: "🍇",
    12: "🥭", 13: "🍌", 14: "🍎", 15: "🫘", 16: "🫘",
    17: "🫛", 18: "🫘", 19: "🫛", 20: "🫘",
    21: "🫛", 22: "☕"
}

# Input validation ranges
VALIDATION_RANGES = {
    'nitrogen': {'min': 0, 'max': 140, 'unit': 'kg/ha'},
    'phosphorus': {'min': 5, 'max': 145, 'unit': 'kg/ha'},
    'potassium': {'min': 5, 'max': 205, 'unit': 'kg/ha'},
    'temperature': {'min': 8, 'max': 44, 'unit': '°C'},
    'humidity': {'min': 14, 'max': 100, 'unit': '%'},
    'ph': {'min': 3.5, 'max': 9.9, 'unit': ''},
    'rainfall': {'min': 20, 'max': 300, 'unit': 'mm'}
}

# Global variables for ML models
model = None
min_max_scaler = None
standard_scaler = None

def load_models():
    """Load machine learning models and scalers."""
    global model, min_max_scaler, standard_scaler
    
    try:
        model = pickle.load(open('model.pkl', 'rb'))
        min_max_scaler = pickle.load(open('minmaxscaler.pkl', 'rb'))
        standard_scaler = pickle.load(open('standardscaler.pkl', 'rb'))
        logger.info("✅ ML models loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")
        return False

def validate_input(value, name, min_val, max_val):
    """
    Validate individual input values.
    
    Args:
        value: Input value to validate
        name: Name of the parameter
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        float: Validated value
        
    Raises:
        ValueError: If value is invalid or out of range
    """
    try:
        val = float(value)
        if val < min_val or val > max_val:
            raise ValueError(f"{name} must be between {min_val} and {max_val}")
        return val
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid {name}: {str(e)}")

def predict_crop(features):
    """
    Predict crop recommendation based on input features.
    
    Args:
        features: List of 7 agricultural parameters
        
    Returns:
        dict: Prediction result with crop name, icon, and message
    """
    try:
        # Reshape and scale features
        feature_array = np.array(features).reshape(1, -1)
        scaled_features = min_max_scaler.transform(feature_array)
        final_features = standard_scaler.transform(scaled_features)
        
        # Make prediction
        prediction = model.predict(final_features)
        
        # Get crop details
        crop_name = CROP_DICT.get(prediction[0], "Unknown Crop")
        crop_icon = CROP_ICONS.get(prediction[0], "🌱")
        
        return {
            'crop_name': crop_name,
            'crop_icon': crop_icon,
            'message': f"{crop_name} is the best crop to be cultivated with these conditions!",
            'confidence': 'High',
            'image_url': url_for('static', filename='crop_images/default.jpg'),
            'success': True
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

@app.route('/')
def index():
    """Render the main application page."""
    return render_template("index.html")

@app.route("/predict", methods=['POST'])
def predict():
    """Handle crop prediction requests."""
    try:
        # Check if models are loaded
        if not all([model, min_max_scaler, standard_scaler]):
            logger.error("Models not properly loaded")
            return render_template('index.html', result={
                'error': True,
                'message': "Error: ML models not loaded properly. Please contact support."
            })
        
        # Extract and validate input parameters
        try:
            nitrogen = validate_input(
                request.form['Nitrogen'], 'Nitrogen', 
                VALIDATION_RANGES['nitrogen']['min'], 
                VALIDATION_RANGES['nitrogen']['max']
            )
            phosphorus = validate_input(
                request.form['Phosporus'], 'Phosphorus',  # Note: keeping original form field name
                VALIDATION_RANGES['phosphorus']['min'], 
                VALIDATION_RANGES['phosphorus']['max']
            )
            potassium = validate_input(
                request.form['Potassium'], 'Potassium',
                VALIDATION_RANGES['potassium']['min'], 
                VALIDATION_RANGES['potassium']['max']
            )
            temperature = validate_input(
                request.form['Temperature'], 'Temperature',
                VALIDATION_RANGES['temperature']['min'], 
                VALIDATION_RANGES['temperature']['max']
            )
            humidity = validate_input(
                request.form['Humidity'], 'Humidity',
                VALIDATION_RANGES['humidity']['min'], 
                VALIDATION_RANGES['humidity']['max']
            )
            ph = validate_input(
                request.form['Ph'], 'pH',
                VALIDATION_RANGES['ph']['min'], 
                VALIDATION_RANGES['ph']['max']
            )
            rainfall = validate_input(
                request.form['Rainfall'], 'Rainfall',
                VALIDATION_RANGES['rainfall']['min'], 
                VALIDATION_RANGES['rainfall']['max']
            )
        except ValueError as e:
            logger.warning(f"Input validation error: {e}")
            return render_template('index.html', result={
                'error': True,
                'message': str(e)
            })
        
        # Make prediction
        features = [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]
        result = predict_crop(features)
        
        logger.info(f"Successful prediction: {result['crop_name']}")
        return render_template('index.html', result=result)
        
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {e}")
        return render_template('index.html', result={
            'error': True,
            'message': "An unexpected error occurred. Please try again."
        })

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    model_status = all([model, min_max_scaler, standard_scaler])
    return {
        'status': 'healthy' if model_status else 'unhealthy',
        'models_loaded': model_status,
        'version': '2.0.0'
    }

@app.route('/favicon.ico')
def favicon():
    """Serve favicon."""
    return url_for('static', filename='favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('index.html', result={
        'error': True,
        'message': "Page not found. Please use the form above to get crop recommendations."
    }), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {e}")
    return render_template('index.html', result={
        'error': True,
        'message': "Internal server error. Please try again later."
    }), 500

if __name__ == "__main__":
    # Load models on startup
    models_loaded = load_models()
    
    if not models_loaded:
        logger.error("Failed to load models. Exiting...")
        exit(1)
    
    # Configuration for different environments
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"🚀 Starting Crop Recommendation System on {host}:{port}")
    logger.info(f"🔧 Debug mode: {debug_mode}")
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        use_reloader=debug_mode,
        threaded=True
    )
