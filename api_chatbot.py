# api_chatbot.py - REST API for your chatbot
from flask import Flask, request, jsonify
from advanced_chatbot import AdvancedChatbot
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize chatbot
chatbot = AdvancedChatbot()

@app.route('/api/v1/chat', methods=['POST'])
def chat_endpoint():
    """
    Chat API endpoint
    POST /api/v1/chat
    {
        "message": "Hello, how are you?",
        "user_id": "optional_user_id"
    }
    """
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get response from chatbot
        response, intent, mood = chatbot.get_response(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'intent': intent,
            'mood': mood,
            'user_id': user_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'chatbot-api'})

@app.route('/api/v1/intents', methods=['GET'])
def get_intents():
    """Get available intents"""
    intents = ['greeting', 'booking', 'price', 'complaint', 'help', 'thanks', 'farewell', 'emotional']
    return jsonify({'intents': intents})

@app.route('/api/v1/process_batch', methods=['POST'])
def process_batch():
    """Process multiple messages at once"""
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        
        results = []
        for msg in messages:
            response, intent, mood = chatbot.get_response(msg)
            results.append({
                'input': msg,
                'response': response,
                'intent': intent,
                'mood': mood
            })
        
        return jsonify({'success': True, 'results': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Chatbot REST API Server")
    print("=" * 60)
    print("\n📍 API Endpoints:")
    print("   POST   /api/v1/chat      - Send a message")
    print("   GET    /api/v1/health    - Health check")
    print("   GET    /api/v1/intents   - Get available intents")
    print("   POST   /api/v1/process_batch - Process multiple messages")
    print("\n📍 Server running at: http://localhost:5001")
    print("📍 Press Ctrl+C to stop\n")
    
    app.run(debug=True, port=5001)