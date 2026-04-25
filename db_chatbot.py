# db_chatbot.py - With SQLite database to remember users
import json
import random
import sqlite3
from datetime import datetime
from collections import deque
from textblob import TextBlob

class DatabaseChatbot:
    def __init__(self, db_name="chatbot_memory.db"):
        # Initialize database
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
        
        # Load your existing chatbot responses
        self.responses = {
            # [Copy your responses dictionary from advanced_chatbot.py]
            'greeting': {
                'positive': ["Hello! Great to see you happy! 😊"],
                'negative': ["Hello. I'm here to help. 💙"],
                'neutral': ["Hello! How can I help you today?"]
            }
            # Add more responses...
        }
        
        # Emotion words
        self.positive_emotions = ['happy', 'excited', 'great', 'wonderful', 'awesome']
        self.negative_emotions = ['sad', 'tired', 'angry', 'frustrated', 'upset']
        
        self.context_memory = deque(maxlen=5)
    
    def create_tables(self):
        """Create database tables for storing conversations"""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                total_conversations INTEGER DEFAULT 0
            )
        ''')
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                conv_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_message TEXT,
                bot_response TEXT,
                intent TEXT,
                mood TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                preferred_language TEXT DEFAULT 'en',
                notification_enabled BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        self.conn.commit()
        print("✓ Database tables created successfully")
    
    def get_or_create_user(self, username="anonymous"):
        """Get existing user or create new one"""
        cursor = self.conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            # Update last seen
            cursor.execute("UPDATE users SET last_seen = ? WHERE user_id = ?", 
                          (datetime.now(), user_id))
        else:
            # Create new user
            cursor.execute("INSERT INTO users (username, first_seen, last_seen) VALUES (?, ?, ?)",
                          (username, datetime.now(), datetime.now()))
            user_id = cursor.lastrowid
            # Create default preferences
            cursor.execute("INSERT INTO user_preferences (user_id) VALUES (?)", (user_id,))
            print(f"✓ Welcome new user: {username}!")
        
        self.conn.commit()
        return user_id
    
    def save_conversation(self, user_id, user_message, bot_response, intent, mood):
        """Save conversation to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (user_id, user_message, bot_response, intent, mood, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, user_message, bot_response, intent, mood, datetime.now()))
        self.conn.commit()
    
    def get_conversation_history(self, user_id, limit=10):
        """Retrieve user's conversation history"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_message, bot_response, intent, mood, timestamp
            FROM conversations
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        
        history = cursor.fetchall()
        return history
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        cursor = self.conn.cursor()
        
        # Get total conversations
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE user_id = ?", (user_id,))
        total_chats = cursor.fetchone()[0]
        
        # Get mood distribution
        cursor.execute('''
            SELECT mood, COUNT(*) as count 
            FROM conversations 
            WHERE user_id = ? 
            GROUP BY mood
        ''', (user_id,))
        mood_stats = cursor.fetchall()
        
        # Get intent distribution
        cursor.execute('''
            SELECT intent, COUNT(*) as count 
            FROM conversations 
            WHERE user_id = ? 
            GROUP BY intent
        ''', (user_id,))
        intent_stats = cursor.fetchall()
        
        return {
            'total_conversations': total_chats,
            'mood_distribution': dict(mood_stats),
            'intent_distribution': dict(intent_stats)
        }
    
    def detect_mood(self, text):
        """Detect mood from text"""
        text_lower = text.lower()
        for word in self.negative_emotions:
            if word in text_lower:
                return "negative"
        for word in self.positive_emotions:
            if word in text_lower:
                return "positive"
        return "neutral"
    
    def detect_intent(self, text):
        """Detect intent (simplified)"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['hello', 'hi', 'hey']):
            return "greeting"
        if any(word in text_lower for word in ['book', 'room']):
            return "booking"
        if any(word in text_lower for word in ['price', 'cost']):
            return "price"
        return "general"
    
    def get_response(self, user_message, username="anonymous"):
        """Get response and save to database"""
        # Get or create user
        user_id = self.get_or_create_user(username)
        
        # Detect mood and intent
        mood = self.detect_mood(user_message)
        intent = self.detect_intent(user_message)
        
        # Generate response (simplified)
        if intent == "greeting":
            response = "Hello! How can I help you today?"
        elif intent == "booking":
            response = "I can help you book a room. What dates?"
        elif intent == "price":
            response = "Our rooms range from $100-$300 per night."
        else:
            response = "How can I assist you?"
        
        # Save to database
        self.save_conversation(user_id, user_message, response, intent, mood)
        
        return response, intent, mood
    
    def show_user_history(self, username="anonymous"):
        """Display user's conversation history"""
        user_id = self.get_or_create_user(username)
        history = self.get_conversation_history(user_id)
        stats = self.get_user_stats(user_id)
        
        print(f"\n📊 STATISTICS for {username}:")
        print(f"   Total conversations: {stats['total_conversations']}")
        print(f"   Mood distribution: {stats['mood_distribution']}")
        print(f"   Intent distribution: {stats['intent_distribution']}")
        
        print(f"\n📝 Recent conversations:")
        for msg, resp, intent, mood, timestamp in history[:5]:
            print(f"   [{timestamp}] You: {msg[:50]}")
            print(f"   → Bot: {resp[:50]}")
            print(f"   (Intent: {intent}, Mood: {mood})")
    
    def close(self):
        """Close database connection"""
        self.conn.close()

# Interactive chat with database
def interactive_db_chat():
    print("=" * 60)
    print("🤖 DATABASE-POWERED CHATBOT - Remembers You!")
    print("=" * 60)
    
    username = input("\nWhat's your name? ").strip() or "anonymous"
    bot = DatabaseChatbot()
    
    print(f"\n✨ Welcome {username}! I remember our conversations!")
    print("📝 Type 'quit' to exit")
    print("📝 Type 'history' to see our past conversations")
    print("📝 Type 'stats' to see your statistics\n")
    
    while True:
        user_input = input("👤 You: ").strip()
        
        if user_input.lower() == 'quit':
            print("\n🤖 Bot: Goodbye! I'll remember our conversation!")
            break
        
        if user_input.lower() == 'history':
            bot.show_user_history(username)
            continue
        
        if user_input.lower() == 'stats':
            stats = bot.get_user_stats(bot.get_or_create_user(username))
            print(f"\n📊 Your Stats:")
            print(f"   Total chats: {stats['total_conversations']}")
            print(f"   Moods: {dict(stats['mood_distribution'])}")
            continue
        
        response, intent, mood = bot.get_response(user_input, username)
        print(f"🤖 Bot: {response}")
    
    bot.close()

if __name__ == "__main__":
    interactive_db_chat()