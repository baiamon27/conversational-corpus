# web_chatbot.py - Flask web interface for your chatbot
from flask import Flask, render_template, request, jsonify, session
from advanced_chatbot import AdvancedChatbot
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-this'

# Initialize your chatbot
chatbot = AdvancedChatbot()

# Store conversation history for sessions
conversation_history = {}

@app.route('/')
def index():
    """Serve the chat interface"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat API requests"""
    data = request.json
    user_message = data.get('message', '')
    
    # Get or create session history
    session_id = session.get('session_id', 'default')
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    # Get bot response
    response, intent, mood = chatbot.get_response(user_message)
    
    # Store in history
    conversation_history[session_id].append({
        'user': user_message,
        'bot': response,
        'intent': intent,
        'mood': mood,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({
        'response': response,
        'intent': intent,
        'mood': mood
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history"""
    session_id = session.get('session_id', 'default')
    history = conversation_history.get(session_id, [])
    return jsonify(history)

@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    session_id = session.get('session_id', 'default')
    conversation_history[session_id] = []
    return jsonify({'status': 'cleared'})

if __name__ == '__main__':
    print("=" * 60)
    print("🌐 Starting Web Chatbot Server")
    print("=" * 60)
    print("\n📍 Access the chatbot at: http://localhost:5000")
    print("📍 Press Ctrl+C to stop the server\n")
    app.run(debug=True, port=5000)