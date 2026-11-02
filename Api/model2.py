from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import io
import logging
import os
import time
import base64
import json
import random

# Flask app and configurations
app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variables
model = None
model_loaded = False
model_load_error = None
model_load_time = None
prediction_count = 0

# Load intents data
def load_intents():
    try:
        with open('intents.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error loading intents.json: {str(e)}")
        return None

intents_data = load_intents()

# Load ML model
def load_ml_model():
    global model, model_loaded, model_load_error, model_load_time
    try:
        logging.info("Loading the ML model...")
        model_path = 'model_fer2013.h5'
        if not os.path.exists(model_path):
            model_load_error = f"Model file not found at {model_path}"
            logging.error(model_load_error)
            return
        model = load_model(model_path, compile=False)
        model_loaded = True
        model_load_time = time.time()
        logging.info("Model loaded successfully.")
    except Exception as e:
        model_load_error = f"Failed to load model: {str(e)}"
        logging.error(model_load_error, exc_info=True)

def get_emotion_response(emotion):
    if not intents_data:
        return "I apologize, but I'm having trouble accessing my responses right now."
    
    # Convert emotion to lowercase for case-insensitive matching
    emotion = emotion.lower()
    
    # First try to match exact emotion tag
    for intent in intents_data['intents']:
        if intent['tag'].lower() == emotion:
            return random.choice(intent['responses'])
    
    # If no emotion match found, use neutral responses
    neutral_responses = next(
        (intent['responses'] for intent in intents_data['intents'] 
         if intent['tag'].lower() == 'neutral'),
        ["I'm here to listen. Would you like to share more?"]
    )
    return random.choice(neutral_responses)

def get_response_for_text(text, current_emotion):
    if not intents_data:
        return "I apologize, but I'm having trouble accessing my responses right now."
    
    text = text.lower()
    current_emotion = current_emotion.lower()
    
    # First check if the text matches any specific patterns
    for intent in intents_data['intents']:
        for pattern in intent['patterns']:
            if pattern.lower() in text:
                return random.choice(intent['responses'])
    
    # If no pattern match, provide an emotion-appropriate response
    return get_emotion_response(current_emotion)

@app.route('/predict', methods=['POST'])
def predict():
    global prediction_count

    if not model_loaded:
        logging.error("Model not loaded")
        return jsonify({'error': 'Model not loaded. Please check server logs.'}), 503

    if 'image' not in request.files:
        logging.error("No image file provided in the request")
        return jsonify({'error': 'No image file provided'}), 400

    try:
        # Read and preprocess the image
        img_data = request.files['image'].read()
        img = Image.open(io.BytesIO(img_data)).convert('L').resize((48, 48))
        img_array = np.array(img) / 255.0
        img_array = img_array.reshape(1, 48, 48, 1)

        # Make prediction
        prediction = model.predict(img_array)
        emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        result = {emotion: float(score) for emotion, score in zip(emotion_labels, prediction[0])}
        dominant_emotion = max(result, key=result.get)

        # Get initial response based on emotion
        initial_response = get_emotion_response(dominant_emotion)

        # Update metrics
        prediction_count += 1
        logging.info(f"Prediction result: {result}")

        return jsonify({
            "emotion": dominant_emotion,
            "confidence": result[dominant_emotion],
            "initial_response": initial_response
        })

    except Exception as e:
        logging.error(f"Error in predict function: {str(e)}", exc_info=True)
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("text", "")
        emotion = data.get("emotion", "neutral")
        
        # Get appropriate response based on user input and emotion
        response = get_response_for_text(user_input, emotion)
        
        logging.info(f"Chat response generated for emotion {emotion}: {response}")
        return jsonify({"response": response})
    except Exception as e:
        logging.error(f"Error in chat function: {str(e)}", exc_info=True)
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# Health check route remains the same
@app.route('/health', methods=['GET'])
def health_check():
    if model_loaded:
        uptime = time.time() - model_load_time if model_load_time else None
        return jsonify({
            'status': 'OK',
            'message': 'Model loaded and ready',
            'uptime': uptime
        }), 200
    else:
        return jsonify({
            'status': 'Not Ready',
            'message': model_load_error or 'Model not loaded'
        }), 503

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    load_ml_model()
    logging.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)