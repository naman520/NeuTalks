from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# Load emotion detection model
emotion_model = pipeline("text-classification", model="nateraw/bert-base-uncased-emotion")
# Load chatbot model
chatbot_model = pipeline("text-generation", model="microsoft/DialoGPT-small")

@app.route('/predict_emotion', methods=['POST'])
def predict_emotion():
    data = request.json
    user_input = data.get("text", "")
    emotion = emotion_model(user_input)
    return jsonify(emotion)

@app.route('/chat', methods=['POST'])
def chat():
    get_emotion = model.predict
    data = request.json
    user_input = data.get("text", "")
    emotion = data.get("emotion", "neutral")  # Use detected emotion as context

    # Generate response based on user input and emotion
    response = chatbot_model(f"{emotion}: {user_input}", max_length=50)
    return jsonify({"response": response[0]["generated_text"]})

if __name__ == '__main__':
    app.run(debug=True)
