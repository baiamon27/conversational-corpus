import json
import random
from typing import List, Dict, Any
from datetime import datetime

class DataCollector:
    def __init__(self):
        self.conversations = []
        
    def generate_synthetic_conversations(self, num_conversations: int = 100) -> List[Dict]:
        """Generate synthetic conversation data for prototyping"""
        
        topics = [
            "customer_support", "booking", "product_inquiry", 
            "technical_help", "general_chat", "complaint"
        ]
        
        intents = {
            "greeting": ["hi", "hello", "hey there", "good morning"],
            "farewell": ["bye", "goodbye", "see you", "take care"],
            "help": ["can you help me", "I need assistance", "help please"],
            "inquiry": ["tell me about", "what is", "how does", "when will"],
            "complaint": ["not working", "bad experience", "issue with"],
            "confirmation": ["yes", "correct", "that's right", "okay"]
        }
        
        responses = {
            "greeting": ["Hello! How can I help you?", "Hi there!", "Welcome!"],
            "help": ["Sure, I'd be happy to help.", "Let me assist you with that."],
            "inquiry": ["Here's the information you requested.", "Let me explain that."],
            "apology": ["I apologize for the inconvenience.", "Sorry about that."],
            "farewell": ["Have a great day!", "Goodbye!"]
        }
        
        for i in range(num_conversations):
            conv_id = f"conv_{i+1:04d}"
            topic = random.choice(topics)
            turns = []
            
            num_turns = random.randint(4, 12)
            current_intent = "greeting"
            
            for turn in range(num_turns):
                if turn == 0:
                    # User starts
                    intent = "greeting"
                    text = random.choice(intents[intent])
                    speaker = "user"
                elif turn % 2 == 1:
                    # Bot response
                    speaker = "bot"
                    if current_intent in responses:
                        text = random.choice(responses[current_intent])
                    else:
                        text = "I understand. Please continue."
                else:
                    # User continues
                    speaker = "user"
                    # Rotate through intents
                    intent_list = list(intents.keys())
                    current_intent = random.choice(intent_list)
                    text = random.choice(intents[current_intent])
                
                turns.append({
                    "turn_id": turn,
                    "speaker": speaker,
                    "text": text,
                    "intent": current_intent if speaker == "user" else "response",
                    "timestamp": datetime.now().isoformat()
                })
            
            self.conversations.append({
                "conversation_id": conv_id,
                "topic": topic,
                "domain": "general",
                "num_turns": num_turns,
                "turns": turns,
                "metadata": {
                    "created_date": datetime.now().isoformat(),
                    "source": "synthetic",
                    "language": "en"
                }
            })
        
        return self.conversations
    
    def load_json_data(self, filepath: str) -> List[Dict]:
        """Load existing conversation data from JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.conversations.extend(data)
        return self.conversations
    
    def save_raw_data(self, filepath: str):
        """Save collected data to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.conversations, f, indent=2)
        print(f"Saved {len(self.conversations)} conversations to {filepath}")

if __name__ == "__main__":
    # Test data collection
    collector = DataCollector()
    collector.generate_synthetic_conversations(50)
    collector.save_raw_data("../data/raw/raw_conversations.json")