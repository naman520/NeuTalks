from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import io
import logging
import threading
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(level=logging.INFO)

# Global variable for the model
model = None

# Load model in a separate thread to avoid blocking
def load_model_thread():
    global model
    try:
        model = load_model('model_fer2013.h5')
        logging.info("Model loaded successfully")
    except Exception as e:
        logging.error(f"Failed to load model: {str(e)}")
        raise

threading.Thread(target=load_model_thread).start()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/predict', methods=['POST'])
def predict():
    logging.info("Received prediction request")
    if 'image' not in request.files:
        logging.error("No image file provided")
        return jsonify({'error': 'No image file provided'}), 400
    try:
        img_data = request.files['image'].read()
        img = Image.open(io.BytesIO(img_data))
        
        # Preprocess the image (adjust based on your model's requirements)
        img = img.convert('L').resize((48, 48))
        img_array = np.array(img) / 255.0
        img_array = img_array.reshape(1, 48, 48, 1)
        
        if model is None:
            logging.error("Model not loaded yet")
            return jsonify({'error': 'Model not loaded yet. Please try again later.'}), 503

        prediction = model.predict(img_array)
        emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        result = {emotion: float(score) for emotion, score in zip(emotion_labels, prediction[0])}
        
        logging.info("Prediction successful")
        return jsonify(result)
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    logging.info("Received feedback")
    data = request.json
    if data and 'isCorrect' in data:
        # Here you would typically store this feedback or use it to improve the model
        # For now, we'll just log it
        logging.info(f"Feedback received: {'correct' if data['isCorrect'] else 'incorrect'}")
        return jsonify({"status": "Feedback received"}), 200
    else:
        logging.error("Invalid feedback data")
        return jsonify({"error": "Invalid feedback data"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, threaded=True)