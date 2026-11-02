import logging
from tensorflow.keras.models import load_model
import os

def load_ml_model():
    global model, model_loaded, model_load_error
    try:
        logging.info("Attempting to load model...")
        model_path = 'model_fer2013.h5'  # Update this path
        if not os.path.exists(model_path):
            model_load_error = f"Model file not found at {model_path}"
            logging.error(model_load_error)
            return
        model = load_model(model_path)
        model_loaded = True
        logging.info("Model loaded successfully")
    except Exception as e:
        model_load_error = f"Failed to load model: {str(e)}"
        logging.error(model_load_error, exc_info=True)