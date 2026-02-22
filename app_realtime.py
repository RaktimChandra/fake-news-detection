from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import os
import logging
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize model and tokenizer
try:
    logger.info('Loading BERT tokenizer...')
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    
    logger.info('Loading trained model...')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f'Using device: {device}')
    
    model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
    
    if os.path.exists('enhanced_model.pt'):
        try:
            state_dict = torch.load('enhanced_model.pt', map_location=device, weights_only=True)
            if isinstance(state_dict, dict):
                if 'state_dict' in state_dict:
                    state_dict = state_dict['state_dict']
                elif 'model_state_dict' in state_dict:
                    state_dict = state_dict['model_state_dict']
                model.load_state_dict(state_dict, strict=False)
                logger.info('Model loaded successfully')
        except Exception as e:
            logger.error(f'Error loading model: {str(e)}')
            raise
    
    model = model.to(device)
    model.eval()
    logger.info('Model ready')
except Exception as e:
    logger.error(f'Error initializing model: {str(e)}')
    model = None
    tokenizer = None

def extract_article_from_url(url):
    """
    Extract article content from a URL
    Returns: (title, text, error)
    """
    try:
        logger.info(f'Fetching URL: {url}')
        
        # Add headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to extract title
        title = ''
        if soup.find('h1'):
            title = soup.find('h1').get_text().strip()
        elif soup.find('title'):
            title = soup.find('title').get_text().strip()
        
        # Try to extract article text
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            script.decompose()
        
        # Try common article containers
        article_text = ''
        article_selectors = [
            'article',
            '.article-content',
            '.article-body',
            '.post-content',
            '.entry-content',
            '#article-body',
            '.story-body',
            'main'
        ]
        
        for selector in article_selectors:
            if article_text:
                break
            elements = soup.select(selector)
            if elements:
                article_text = ' '.join([elem.get_text().strip() for elem in elements])
        
        # Fallback: get all paragraph text
        if not article_text:
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text().strip() for p in paragraphs])
        
        # Clean text
        article_text = re.sub(r'\s+', ' ', article_text).strip()
        
        if len(article_text) < 100:
            return None, None, 'Could not extract enough text from the URL. Please try copying the article text directly.'
        
        logger.info(f'Successfully extracted article: {len(article_text)} characters')
        return title, article_text, None
        
    except requests.Timeout:
        return None, None, 'Request timed out. Please try again or paste the article text directly.'
    except requests.RequestException as e:
        return None, None, f'Error fetching URL: {str(e)}'
    except Exception as e:
        return None, None, f'Error processing article: {str(e)}'

def predict_fake_news(text):
    """
    Predict if news is fake or real
    Returns: (prediction, confidence, processing_time)
    """
    try:
        start_time = time.time()
        
        if model is None or tokenizer is None:
            logger.error('Model not loaded')
            return None, None, None
        
        # Prepare input
        inputs = tokenizer(text, 
                         truncation=True, 
                         padding=True, 
                         max_length=512,
                         return_tensors='pt')
        
        # Move to device
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Predict
        model.eval()
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            
            # Get predictions
            fake_prob = float(probabilities[0][0])
            real_prob = float(probabilities[0][1])
            
            # Determine result
            if real_prob > fake_prob:
                prediction = 1  # Real
                confidence = round(real_prob * 100, 2)
            else:
                prediction = 0  # Fake
                confidence = round(fake_prob * 100, 2)
        
        processing_time = round(time.time() - start_time, 3)
        
        logger.info(f'Prediction: {"REAL" if prediction == 1 else "FAKE"} ({confidence}%) in {processing_time}s')
        
        return prediction, confidence, processing_time
        
    except Exception as e:
        logger.error(f'Prediction error: {str(e)}')
        return None, None, None

@app.route('/')
def index():
    return render_template('index_realtime.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        text = data.get('text', '').strip()
        
        # Determine if URL or text
        if url:
            # URL provided - fetch article
            logger.info('Processing URL...')
            title, article_text, error = extract_article_from_url(url)
            
            if error:
                return jsonify({'error': error}), 400
            
            # Combine title and text
            full_text = f"{title}. {article_text}"
            source = url
            
        elif text:
            # Direct text provided
            logger.info('Processing direct text...')
            full_text = text
            source = 'Direct input'
            
        else:
            return jsonify({'error': 'Please provide either a URL or article text'}), 400
        
        # Check text length
        if len(full_text) < 50:
            return jsonify({'error': 'Article too short (minimum 50 characters)'}), 400
        
        # Make prediction
        prediction, confidence, processing_time = predict_fake_news(full_text)
        
        if prediction is None:
            return jsonify({'error': 'Error making prediction'}), 500
        
        # Prepare response
        result = {
            'success': True,
            'prediction': 'REAL' if prediction == 1 else 'FAKE',
            'confidence': confidence,
            'processing_time': processing_time,
            'source': source,
            'text_length': len(full_text),
            'word_count': len(full_text.split()),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f'Error in analyze: {str(e)}')
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'device': str(next(model.parameters()).device) if model else 'N/A',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    logger.info('Starting Real-Time Fake News Detection Server...')
    app.run(host='0.0.0.0', port=5000, debug=True)
