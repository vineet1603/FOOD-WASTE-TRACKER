# app.py
from flask import Flask, render_template, request, jsonify
import requests
import os
from chatbot_logic import get_chatbot_response

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

API_KEY = 'sk-a2618208aadc410481a98feea728ec55'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Send image to API
        response = requests.post(
            f'https://api.spoonacular.com/food/images/analyze',
            headers={'Content-Type': 'application/json'},
            params={'apiKey': API_KEY},
            json={"image": filepath}
        )

        result = response.json()
        # Fake expiry logic (real one should be smarter)
        expiry_days = 3 if 'fruit' in result.get('category', '').lower() else 5

        return jsonify({
            'foodName': result.get('category', 'Unknown Food'),
            'expiry': f"Best before {expiry_days} days"
        })

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    bot_response = get_chatbot_response(user_message)
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
