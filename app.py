from flask import Flask, render_template, request, jsonify
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

# Create template file
with open('templates/index.html', 'w') as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Fake News Detection</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        textarea {
            width: 100%;
            height: 150px;
            margin: 10px 0;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 4px;
        }
        .true {
            background-color: #dff0d8;
            color: #3c763d;
        }
        .fake {
            background-color: #f2dede;
            color: #a94442;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Fake News Detection</h1>
        <form method="POST">
            <textarea name="text" placeholder="Enter news article text here..."></textarea>
            <button type="submit">Analyze</button>
        </form>
        {% if prediction is not none %}
        <div class="result {% if prediction == 1 %}true{% else %}fake{% endif %}">
            <h3>Analysis Result:</h3>
            <p>This article appears to be: <strong>{% if prediction == 1 %}TRUE{% else %}FAKE{% endif %}</strong></p>
            <p>Confidence: {{ confidence }}%</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
    """)

# Initialize model and tokenizer
try:
    logging.info('Loading BERT tokenizer...')
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    
    logging.info('Loading trained model...')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logging.info(f'Using device: {device}')
    
    # Create base model
    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
    
    if os.path.exists('enhanced_model.pt'):
        try:
            # Load state dict with safe loading
            state_dict = torch.load('enhanced_model.pt', map_location=device, weights_only=True)
            if isinstance(state_dict, dict):
                if 'state_dict' in state_dict:
                    state_dict = state_dict['state_dict']
                model.load_state_dict(state_dict, strict=False)
                logging.info('Model state loaded successfully')
                
                # Verify model parameters
                param_count = sum(p.numel() for p in model.parameters() if p.requires_grad)
                logging.info(f'Model loaded with {param_count:,} trainable parameters')
            else:
                logging.error('Invalid model format')
                raise ValueError('Invalid model format')
        except Exception as e:
            logging.error(f'Error loading model state: {str(e)}')
            raise
    else:
        logging.error('Model file not found')
        raise FileNotFoundError('enhanced_model.pt not found')
    
    model = model.to(device)
    model.eval()
    logging.info(f'Model ready on device: {device}')
except Exception as e:
    logging.error(f'Error loading model: {str(e)}')
    model = None
    tokenizer = None

def predict_fake_news(text):
    try:
        if model is None or tokenizer is None:
            logging.error('Model or tokenizer not loaded')
            return None, None
            
        # Prepare input
        inputs = tokenizer(text, 
                         truncation=True, 
                         padding=True, 
                         max_length=512,  # Increased max length
                         return_tensors='pt')
        
        # Move inputs to the same device as model
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Make prediction
        model.eval()
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            
            # Get probabilities for both classes
            # In BERT model, usually first class (0) is negative/fake, second class (1) is positive/real
            fake_prob = float(probabilities[0][0])
            real_prob = float(probabilities[0][1])
            
            # Determine prediction and confidence
            # We're flipping the logic here because in our dataset:
            # 0 = Fake news, 1 = Real news
            if real_prob > fake_prob:
                prediction = 0  # Fake
                confidence = round(real_prob * 100, 2)
            else:
                prediction = 1  # Real
                confidence = round(fake_prob * 100, 2)
                
            logging.info(f'Raw probabilities - Fake: {fake_prob:.4f}, Real: {real_prob:.4f}')
            logging.info(f'Final prediction: {prediction} (Fake if 0, Real if 1) with confidence {confidence}%')
            
            return prediction, confidence
    except Exception as e:
        logging.error(f'Prediction error: {str(e)}')
        return None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        prediction = None
        confidence = None
        error = None
        text = ''

        if request.method == 'POST':
            text = request.form.get('text', '').strip()
            if text:
                prediction, confidence = predict_fake_news(text)
                if prediction is None:
                    error = 'Error processing your request. Please try again.'
            else:
                error = 'Please enter some text to analyze.'

        return render_template('index.html',
                             prediction='TRUE' if prediction == 1 else 'FAKE' if prediction is not None else None,
                             confidence=confidence,
                             error=error,
                             text=text)
    except Exception as e:
        logging.error(f'Error in index route: {str(e)}')
        return 'Internal server error', 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get text from form data or JSON
        if request.is_json:
            data = request.get_json()
            text = data.get('text', '')
        else:
            text = request.form.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        # Make prediction
        prediction, confidence = predict_fake_news(text)
        
        if prediction is None:
            return jsonify({'error': 'Prediction failed'}), 500
            
        # Note: prediction of 0 means Fake, 1 means Real
        result = {
            'prediction': 'TRUE' if prediction == 1 else 'FAKE',
            'confidence': confidence
        }
        
        if request.is_json:
            return jsonify(result)
        else:
            return render_template('index.html', 
                                 result=result,
                                 text=text)
    except Exception as e:
        logging.error(f'Error in analyze endpoint: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        logging.info('Starting Flask server...')
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logging.error(f'Error starting server: {str(e)}')
