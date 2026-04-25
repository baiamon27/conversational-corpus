# advanced_chatbot.py - With Joke Support and Better Intent Detection
import random
import re
from collections import deque
from textblob import TextBlob

class AdvancedChatbot:
    def __init__(self):
        # Expanded emotion word lists
        self.positive_emotions = [
            'happy', 'excited', 'great', 'wonderful', 'awesome', 'amazing', 
            'fantastic', 'good', 'glad', 'delighted', 'joyful', 'cheerful',
            'ecstatic', 'thrilled', 'pleased', 'satisfied', 'content',
            'optimistic', 'hopeful', 'grateful', 'blessed', 'fine', 'healthy'
        ]
        
        self.negative_emotions = [
            'sad', 'tired', 'exhausted', 'angry', 'frustrated', 'upset', 
            'terrible', 'awful', 'bad', 'depressed', 'anxious', 'stressed',
            'lonely', 'hurt', 'miserable', 'disappointed', 'confused',
            'worried', 'scared', 'nervous', 'overwhelmed', 'unhappy',
            'gloomy', 'heartbroken', 'devastated', 'annoyed'
        ]
        
        self.affirmative_words = ['yes', 'ok', 'okay', 'sure', 'yeah', 'yep', 'fine']
        self.negative_words = ['no', 'nope', 'not', 'never']
        
        # Jokes collection
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything! 😄",
            "What do you call a fake noodle? An impasta! 🍝",
            "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
            "What do you call a bear with no teeth? A gummy bear! 🐻",
            "Why don't eggs tell jokes? They'd crack each other up! 🥚",
            "What's the best thing about Switzerland? I don't know, but the flag is a big plus! 🇨🇭",
            "Why did the math book look so sad? Because it had too many problems! 📚",
            "What do you call a fish wearing a bowtie? Sofishticated! 🐠",
            "Why did the cookie go to the doctor? Because it felt crumbly! 🍪",
            "What do you call a sleeping bull? A bulldozer! 🐂"
        ]
        
        self.context_memory = deque(maxlen=5)
        self.user_mood = "neutral"
        self.last_question = None
        
        # Mood-aware responses
        self.responses = {
            'greeting': {
                'positive': ["Hello! Great to see you happy! 😊 How can I help?", "Hi there! You seem in a good mood! 🌟 What can I do for you?"],
                'negative': ["Hello. I'm here to help if you're having a bad day. 💙", "Hi there. I can see you might be frustrated. Let me help. 🤝"],
                'neutral': ["Hello! How can I help you today?", "Hi there! Welcome!", "Hey! Nice to meet you!"]
            },
            'joke': {
                'positive': ["Here's a joke to make you smile! 😊 ", "Sure! I love telling jokes! 🎉 "],
                'negative': ["I hope this joke makes you feel better! 💙 ", "Let me try to cheer you up! 😊 "],
                'neutral': ["Here's a joke for you! 😄 ", "Sure! Check this out: "]
            },
            'emotional_positive': {
                'positive': ["I'm glad you're feeling happy! 😊 How can I make your day even better?", "That's wonderful to hear! 🎉 What can I help you with?"],
                'negative': ["I hope you feel better soon! 💙 How can I help you today?", "Thanks for sharing. Let me know how I can assist."],
                'neutral': ["I'm glad to hear that! How can I help you?"]
            },
            'emotional_negative': {
                'positive': ["I'm here to help make you feel better! 😊 What's wrong?", "Let me help turn your day around! 🌟 What's bothering you?"],
                'negative': ["I'm sorry you're feeling that way. 💙 I'm here to help. What's wrong?", "I understand. That's tough. 😟 How can I assist you today?"],
                'neutral': ["I hear you. How can I help you today?", "Thanks for sharing. What can I do for you?"]
            },
            'help': {
                'positive': ["I'd be thrilled to help with that! 😊", "Absolutely! I'm happy to assist you! ✨"],
                'negative': ["I understand you need help. Let me make this right. 🤝", "I'm here to help resolve your issue. 💙"],
                'neutral': ["I'd be happy to help with that.", "Let me assist you.", "Sure, what do you need help with?"]
            },
            'booking': {
                'positive': ["Excellent! I'd love to help you book a room! 🏨 What dates?", "Great choice! When would you like to stay? 📅"],
                'negative': ["I understand you need a room. Let me help. 🏨", "I'll help you find a room. What dates?"],
                'neutral': ["I can help you book a room. What dates?", "Let me check availability. When would you like to book?"]
            },
            'price': {
                'positive': ["Great question! Our rooms range from $100-$300 per night. 💰", "I'd be happy to share our rates! ✨"],
                'negative': ["I understand price is a concern. Let me find you the best rate. 💙", "Let me check for discounts. 🤝"],
                'neutral': ["Rooms range from $100-$300 per night.", "Let me check current pricing for you."]
            },
            'affirmative': {
                'positive': ["Great! 😊 What else can I help you with?", "Awesome! Anything else? ✨"],
                'negative': ["Okay. Let me know if you need anything else. 💙", "Alright. I'm here if you need help."],
                'neutral': ["Okay! How else can I assist you?", "Great! What's next?"]
            },
            'negative_response': {
                'positive': ["No problem! Let me know if you change your mind. 😊", "Okay! Feel free to ask if you need anything!"],
                'negative': ["I understand. Let me know if I can help with something else. 💙", "Okay. I'm here if you need me."],
                'neutral': ["Alright. Is there anything else I can help with?"]
            },
            'farewell': {
                'positive': ["Goodbye! Have an amazing day! 😊", "Thanks for chatting! Come back anytime! 🌟"],
                'negative': ["Goodbye. I hope your day gets better. 💙", "Take care. I'm here if you need anything. 🤝"],
                'neutral': ["Goodbye! Have a great day!", "See you later! Take care!"]
            },
            'thanks': {
                'positive': ["You're absolutely welcome! 😊", "My pleasure! Happy to help! ✨"],
                'negative': ["You're welcome. I hope that helped. 💙", "Happy to help. Let me know if you need anything else."],
                'neutral': ["You're welcome!", "Happy to help!", "Anytime!"]
            },
            'unknown': {
                'positive': ["Interesting! Could you tell me more? 😊", "I'm curious! What do you mean? ✨"],
                'negative': ["I want to help. Could you rephrase that? 💙", "I'm having trouble understanding. Can you explain? 🤝"],
                'neutral': ["I'm not sure I understand. Could you rephrase?", "Could you please provide more details?"]
            }
        }
        
        # Keywords for intent detection
        self.greeting_words = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'howdy']
        self.farewell_words = ['bye', 'goodbye', 'see you', 'farewell', 'take care', 'cya']
        self.help_words = ['help', 'assist', 'support', 'can you', 'could you']
        self.booking_words = ['book', 'room', 'reservation', 'hotel', 'accommodation', 'stay', 'need a room']
        self.price_words = ['price', 'cost', 'how much', 'expensive', 'cheap', 'fee', 'rate']
        self.complaint_words = ['broken', 'issue', 'problem', 'not working', 'damage', 'wrong', 'bad']
        self.thanks_words = ['thank', 'thanks', 'appreciate', 'grateful']
        self.joke_words = ['joke', 'funny', 'laugh', 'humor', 'tell me a joke', 'make me laugh']
    
    def detect_mood(self, text):
        """Detect user's mood from text"""
        text_lower = text.lower()
        
        # Check for negative emotions first (stronger signal)
        for word in self.negative_emotions:
            if word in text_lower:
                return "negative"
        
        # Check for positive emotions
        for word in self.positive_emotions:
            if word in text_lower:
                return "positive"
        
        # Use sentiment analysis
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            if polarity > 0.2:
                return "positive"
            elif polarity < -0.1:
                return "negative"
        except:
            pass
        
        return "neutral"
    
    def detect_intent(self, text):
        """Detect intent from user input"""
        text_lower = text.lower()
        
        # Check for joke requests first
        for word in self.joke_words:
            if word in text_lower:
                return "joke"
        
        # Check for affirmative/negative responses
        if any(word in text_lower for word in self.affirmative_words):
            if len(text_lower) < 5:
                return "affirmative"
        
        if any(word in text_lower for word in self.negative_words):
            if len(text_lower) < 5:
                return "negative_response"
        
        # Check for emotional statements
        for word in self.negative_emotions:
            if word in text_lower:
                return "emotional_negative"
        
        for word in self.positive_emotions:
            if word in text_lower:
                return "emotional_positive"
        
        # Check other intents
        if any(word in text_lower for word in self.greeting_words):
            return "greeting"
        if any(word in text_lower for word in self.farewell_words):
            return "farewell"
        if any(word in text_lower for word in self.help_words):
            return "help"
        if any(word in text_lower for word in self.booking_words):
            return "booking"
        if any(word in text_lower for word in self.price_words):
            return "price"
        if any(word in text_lower for word in self.thanks_words):
            return "thanks"
        
        return "unknown"
    
    def get_response(self, user_input):
        """Generate response based on mood and intent"""
        # Detect mood and intent
        mood = self.detect_mood(user_input)
        intent = self.detect_intent(user_input)
        
        # Store in memory
        self.user_mood = mood
        self.context_memory.append({'input': user_input, 'intent': intent, 'mood': mood})
        
        # Special handling for jokes
        if intent == "joke":
            joke = random.choice(self.jokes)
            prefix = random.choice(self.responses['joke'].get(mood, self.responses['joke']['neutral']))
            return prefix + joke, intent, mood
        
        # Special handling for very short inputs without clear intent
        if len(user_input.strip()) < 4 and intent == "unknown":
            if mood == "positive":
                return "I'm glad you're feeling good! 😊 Is there something specific I can help you with?", intent, mood
            elif mood == "negative":
                return "I'm here for you. 💙 Would you like to talk about what's bothering you?", intent, mood
            else:
                return "How can I help you today?", intent, mood
        
        # Get appropriate response
        if intent in self.responses:
            mood_responses = self.responses[intent].get(mood)
            if not mood_responses:
                mood_responses = self.responses[intent].get('neutral', ["How can I help you?"])
        else:
            mood_responses = self.responses['unknown'].get(mood, self.responses['unknown']['neutral'])
        
        response = random.choice(mood_responses)
        
        return response, intent, mood
    
    def get_suggestions(self):
        """Get suggested questions"""
        return [
            "💡 Try these examples:",
            "  • 'hello' - for greeting",
            "  • 'I am sad' - share your feelings",
            "  • 'I am happy' - share your feelings", 
            "  • 'I feel lonely' - share your feelings",
            "  • 'tell me a joke' - hear a funny joke",
            "  • 'I need a room' - make a booking",
            "  • 'What's the price?' - check rates",
            "  • 'thank you' - show appreciation",
            "  • 'goodbye' - end conversation"
        ]

def interactive_chat():
    """Run interactive chat session"""
    print("=" * 60)
    print("🤖 EMOTIONALLY INTELLIGENT CHATBOT")
    print("=" * 60)
    
    bot = AdvancedChatbot()
    
    print("\n✨ I can understand your feelings! Try telling me:")
    print("   • 'I am happy' 😊")
    print("   • 'I am sad' 💙")
    print("   • 'I feel lonely' 💙")
    print("   • 'I am tired' 😴")
    print("   • 'tell me a joke' 😄")
    print("\n   Or ask me for help with bookings, prices, etc.\n")
    
    for suggestion in bot.get_suggestions():
        print(suggestion)
    
    print("\n📝 Type 'quit' to exit")
    print("=" * 60)
    print("\n✅ Ready! How are you feeling today?\n")
    
    while True:
        user_input = input("👤 You: ").strip().lower()
        
        if user_input == 'quit':
            print("\n🤖 Bot: Thank you for chatting! Take care! 👋")
            break
        
        if not user_input:
            print("🤖 Bot: Please type something!")
            continue
        
        response, intent, mood = bot.get_response(user_input)
        
        mood_emoji = {'positive': '😊', 'negative': '💙', 'neutral': '😐'}
        print(f"🤖 Bot: {response} {mood_emoji.get(mood, '')}")

def demo_mode():
    """Demo mode - test all inputs"""
    print("\n" + "=" * 60)
    print("🎯 DEMO MODE - Testing All Inputs")
    print("=" * 60)
    
    bot = AdvancedChatbot()
    
    test_inputs = [
        "hello",
        "I am happy",
        "I am sad",
        "I feel lonely",
        "tell me a joke",
        "make me laugh",
        "I need a room",
        "what's the price?",
        "thank you",
        "goodbye"
    ]
    
    print("\n📋 Testing various inputs:\n")
    
    for test_input in test_inputs:
        mood = bot.detect_mood(test_input)
        intent = bot.detect_intent(test_input)
        response, _, _ = bot.get_response(test_input)
        
        print(f"📝 Input: '{test_input}'")
        print(f"🎭 Mood: {mood.upper()}")
        print(f"🎯 Intent: {intent}")
        print(f"🤖 Response: {response}")
        print("-" * 50)
        print()

if __name__ == "__main__":
    print("\n🎮 CHATBOT MENU")
    print("=" * 35)
    print("1. 💬 Interactive Chat")
    print("2. 🎯 Demo Mode")
    print("3. ❌ Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        interactive_chat()
    elif choice == '2':
        demo_mode()
    else:
        print("Goodbye! 👋")