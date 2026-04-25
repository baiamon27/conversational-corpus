"""
Downstream NLP Applications using the Conversational Corpus
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

class CorpusAnalyzer:
    """Analyze and use the corpus for NLP tasks"""
    
    def __init__(self, corpus_path="data/processed/complete_corpus.json"):
        self.corpus_path = corpus_path
        self.load_corpus()
    
    def load_corpus(self):
        """Load the corpus from JSON file"""
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            self.corpus = json.load(f)
        print(f"✓ Loaded {len(self.corpus)} conversations")
    
    def create_intent_dataset(self):
        """Create dataset for intent classification"""
        intent_data = []
        for conv in self.corpus:
            for turn in conv['turns']:
                if turn['speaker'] == 'user':  # Only user turns for intent
                    intent_data.append({
                        'text': turn['text'],
                        'intent': turn['annotations']['intent']['primary_intent'],
                        'confidence': turn['annotations']['intent']['confidence']
                    })
        return intent_data
    
    def create_dialogue_act_dataset(self):
        """Create dataset for dialogue act recognition"""
        act_data = []
        for conv in self.corpus:
            for turn in conv['turns']:
                act_data.append({
                    'text': turn['text'],
                    'speaker': turn['speaker'],
                    'dialogue_act': turn['annotations']['dialogue_act']
                })
        return act_data
    
    def create_conversation_flows(self):
        """Extract conversation flow patterns"""
        flows = []
        for conv in self.corpus:
            flow = {
                'conversation_id': conv['conversation_id'],
                'domain': conv['domain'],
                'turns': [],
                'intent_sequence': []
            }
            for turn in conv['turns']:
                flow['turns'].append({
                    'speaker': turn['speaker'],
                    'text': turn['text']
                })
                if turn['speaker'] == 'user':
                    flow['intent_sequence'].append(turn['annotations']['intent']['primary_intent'])
            flows.append(flow)
        return flows
    
    def get_intent_statistics(self):
        """Get detailed intent statistics"""
        intent_data = self.create_intent_dataset()
        intent_counts = Counter([d['intent'] for d in intent_data])
        
        print("\n📊 INTENT CLASSIFICATION STATISTICS")
        print("=" * 40)
        print(f"Total user utterances: {len(intent_data)}")
        print(f"Unique intents: {len(intent_counts)}")
        print("\nIntent Distribution:")
        for intent, count in intent_counts.most_common():
            percentage = (count / len(intent_data)) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {intent:12} : {count:3} ({percentage:5.1f}%) {bar}")
        
        return intent_counts
    
    def save_for_training(self):
        """Save datasets in formats ready for ML training"""
        
        # 1. Intent classification dataset (CSV)
        intent_data = self.create_intent_dataset()
        with open('data/processed/intent_dataset.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['text', 'intent', 'confidence'])
            writer.writeheader()
            writer.writerows(intent_data)
        print(f"✓ Intent dataset saved: {len(intent_data)} samples")
        
        # 2. Dialogue act dataset (CSV)
        act_data = self.create_dialogue_act_dataset()
        with open('data/processed/dialogue_act_dataset.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['text', 'speaker', 'dialogue_act'])
            writer.writeheader()
            writer.writerows(act_data)
        print(f"✓ Dialogue act dataset saved: {len(act_data)} samples")
        
        # 3. Training examples for sequence-to-sequence (JSON)
        flows = self.create_conversation_flows()
        training_examples = []
        for flow in flows:
            # Create input-output pairs for response generation
            for i in range(0, len(flow['turns']) - 1, 2):
                if i + 1 < len(flow['turns']):
                    training_examples.append({
                        'input': flow['turns'][i]['text'],  # user input
                        'output': flow['turns'][i+1]['text'],  # bot response
                        'domain': flow['domain']
                    })
        
        with open('data/processed/response_generation_data.json', 'w', encoding='utf-8') as f:
            json.dump(training_examples, f, indent=2, ensure_ascii=False)
        print(f"✓ Response generation data saved: {len(training_examples)} examples")
        
        return intent_data, act_data, training_examples

class SimpleIntentClassifier:
    """A simple rule-based classifier for demonstration"""
    
    def __init__(self, intent_data):
        self.intent_data = intent_data
        self.build_patterns()
    
    def build_patterns(self):
        """Build keyword patterns from training data"""
        self.intent_keywords = defaultdict(set)
        
        for item in self.intent_data:
            intent = item['intent']
            words = item['text'].lower().split()
            # Extract important words (longer than 3 chars)
            keywords = [w for w in words if len(w) > 3]
            self.intent_keywords[intent].update(keywords)
        
        # Convert to list for faster access
        self.intent_keywords = {k: list(v) for k, v in self.intent_keywords.items()}
    
    def predict(self, text):
        """Predict intent for a given text"""
        text_lower = text.lower()
        scores = Counter()
        
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[intent] += 1
        
        if scores:
            return scores.most_common(1)[0][0]
        return "other"
    
    def test_on_examples(self):
        """Test the classifier on example inputs"""
        test_examples = [
            "Hello, how are you?",
            "I need help with my order",
            "Goodbye, see you later",
            "Can you tell me the price?",
            "I want to book a room",
            "My product is broken",
            "Thank you for your help"
        ]
        
        print("\n🎯 INTENT CLASSIFIER DEMO")
        print("=" * 40)
        for text in test_examples:
            intent = self.predict(text)
            print(f"Input: '{text}'")
            print(f"Predicted Intent: {intent}\n")

def analyze_corpus_quality():
    """Analyze the quality and balance of the corpus"""
    
    with open('data/processed/complete_corpus.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    
    print("\n🔍 CORPUS QUALITY ANALYSIS")
    print("=" * 40)
    
    # Calculate statistics
    total_turns = 0
    total_user_turns = 0
    total_bot_turns = 0
    avg_turn_length = []
    
    for conv in corpus:
        total_turns += len(conv['turns'])
        for turn in conv['turns']:
            if turn['speaker'] == 'user':
                total_user_turns += 1
            else:
                total_bot_turns += 1
            avg_turn_length.append(len(turn['text'].split()))
    
    print(f"📊 Dataset Balance:")
    print(f"  User turns: {total_user_turns} ({total_user_turns/total_turns*100:.1f}%)")
    print(f"  Bot turns:  {total_bot_turns} ({total_bot_turns/total_turns*100:.1f}%)")
    print(f"\n📏 Turn Length Analysis:")
    print(f"  Average turn length: {sum(avg_turn_length)/len(avg_turn_length):.1f} words")
    print(f"  Min turn length: {min(avg_turn_length)} words")
    print(f"  Max turn length: {max(avg_turn_length)} words")
    
    # Check domain balance
    domains = Counter([conv['domain'] for conv in corpus])
    print(f"\n🏷️  Domain Balance:")
    for domain, count in domains.items():
        print(f"  {domain}: {count} ({count/len(corpus)*100:.1f}%)")

def generate_sample_app():
    """Generate code for a simple chatbot using the corpus"""
    
    sample_app = '''
# Simple Chatbot using the conversational corpus

import json
import random

class SimpleChatbot:
    def __init__(self, corpus_path="data/processed/complete_corpus.json"):
        with open(corpus_path, 'r', encoding='utf-8') as f:
            self.corpus = json.load(f)
        self.build_response_map()
    
    def build_response_map(self):
        """Build a map of user inputs to bot responses"""
        self.response_map = {}
        for conv in self.corpus:
            turns = conv['turns']
            for i in range(len(turns) - 1):
                if turns[i]['speaker'] == 'user' and turns[i+1]['speaker'] == 'bot':
                    user_input = turns[i]['text'].lower()
                    bot_response = turns[i+1]['text']
                    if user_input not in self.response_map:
                        self.response_map[user_input] = []
                    self.response_map[user_input].append(bot_response)
    
    def get_response(self, user_input):
        """Generate response for user input"""
        user_input_lower = user_input.lower()
        
        # Try exact match
        if user_input_lower in self.response_map:
            return random.choice(self.response_map[user_input_lower])
        
        # Try keyword matching
        for key, responses in self.response_map.items():
            if any(word in user_input_lower for word in key.split()):
                return random.choice(responses)
        
        return "I'm not sure how to respond to that. Could you rephrase?"

# Usage
if __name__ == "__main__":
    bot = SimpleChatbot()
    print("Chatbot ready! Type 'quit' to exit.")
    while True:
        user_input = input("\\nYou: ")
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        response = bot.get_response(user_input)
        print(f"Bot: {response}")
'''
    
    with open('simple_chatbot.py', 'w', encoding='utf-8') as f:
        f.write(sample_app)
    print("\n✓ Sample chatbot application generated: simple_chatbot.py")

# Main execution
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 USING THE CONVERSATIONAL CORPUS FOR NLP APPLICATIONS")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = CorpusAnalyzer()
    
    # Get intent statistics
    intent_counts = analyzer.get_intent_statistics()
    
    # Save datasets for training
    intent_data, act_data, response_data = analyzer.save_for_training()
    
    # Demo intent classifier
    classifier = SimpleIntentClassifier(intent_data)
    classifier.test_on_examples()
    
    # Analyze corpus quality
    analyze_corpus_quality()
    
    # Generate sample chatbot
    generate_sample_app()
    
    print("\n" + "=" * 60)
    print("✅ CORPUS READY FOR DOWNSTREAM APPLICATIONS")
    print("=" * 60)
    print("\nYou can now use this corpus for:")
    print("  1. 🧠 Training intent classification models")
    print("  2. 💬 Building dialogue systems and chatbots")
    print("  3. 📊 Conversation flow analysis")
    print("  4. 🎯 Dialogue act recognition")
    print("  5. 🔄 Response generation")
    print("\nFiles created:")
    print("  • data/processed/intent_dataset.csv")
    print("  • data/processed/dialogue_act_dataset.csv")
    print("  • data/processed/response_generation_data.json")
    print("  • simple_chatbot.py")