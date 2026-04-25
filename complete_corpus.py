"""
Complete Conversational Corpus Builder - Pure Python Implementation
FIXED VERSION - No KeyError issues
"""

import json
import os
import random
import re
from datetime import datetime
from collections import Counter
from typing import List, Dict, Any, Tuple
from pathlib import Path

class CorpusDataCollector:
    """Collect and generate conversation data"""
    
    def __init__(self):
        self.conversations = []
        
    def generate_synthetic_conversations(self, num_conversations: int = 100) -> List[Dict]:
        """Generate synthetic conversation data"""
        
        domains = {
            "customer_support": {
                "user_texts": [
                    "Hi, I need help with my order",
                    "My product is not working properly",
                    "Can you help me return this item?",
                    "When will my package arrive?",
                    "I have a question about my bill",
                    "Hello, can you assist me?",
                    "Thanks for your help",
                    "Goodbye"
                ],
                "bot_texts": [
                    "I'd be happy to help with that",
                    "Let me check your order status",
                    "I apologize for the inconvenience",
                    "Let me transfer you to a specialist",
                    "Thank you for contacting support",
                    "Is there anything else I can help with?",
                    "Have a great day!"
                ]
            },
            "booking": {
                "user_texts": [
                    "I want to book a room",
                    "What are your prices?",
                    "Do you have availability?",
                    "Can I cancel my booking?",
                    "Is breakfast included?",
                    "Hello, I'd like to make a reservation",
                    "Thank you for your help",
                    "Goodbye"
                ],
                "bot_texts": [
                    "Let me check availability",
                    "I can help you book that",
                    "What dates are you looking for?",
                    "Let me show you our options",
                    "Your booking is confirmed",
                    "Would you like to add anything else?",
                    "Thank you for booking with us"
                ]
            },
            "general_chat": {
                "user_texts": [
                    "Hello, how are you?",
                    "Tell me a joke",
                    "What's the weather like?",
                    "Thanks for your help",
                    "That's interesting",
                    "Hi there",
                    "Bye bye",
                    "See you later"
                ],
                "bot_texts": [
                    "I'm doing great, thanks!",
                    "Here's a fun fact for you",
                    "I'm happy to chat with you",
                    "That's a great question",
                    "Thanks for talking with me",
                    "Is there anything you'd like to know?",
                    "Have a wonderful day"
                ]
            }
        }
        
        for i in range(num_conversations):
            conv_id = f"conv_{i+1:04d}"
            domain = random.choice(list(domains.keys()))
            domain_data = domains[domain]
            
            turns = []
            num_turns = random.randint(4, 12)
            
            for turn_id in range(num_turns):
                speaker = "user" if turn_id % 2 == 0 else "bot"
                if speaker == "user":
                    text = random.choice(domain_data["user_texts"])
                else:
                    text = random.choice(domain_data["bot_texts"])
                
                turns.append({
                    "turn_id": turn_id,
                    "speaker": speaker,
                    "text": text,
                    "timestamp": datetime.now().isoformat()
                })
            
            self.conversations.append({
                "conversation_id": conv_id,
                "domain": domain,
                "num_turns": num_turns,
                "turns": turns,
                "metadata": {
                    "created_date": datetime.now().isoformat(),
                    "source": "synthetic",
                    "version": "1.0"
                }
            })
        
        return self.conversations
    
    def save_raw_data(self, filepath: str):
        """Save raw conversations to JSON"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(self.conversations)} conversations to {filepath}")


class CorpusPreprocessor:
    """Preprocess conversations without external dependencies"""
    
    def __init__(self):
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'i', 'you', 'we', 'they',
            'me', 'my', 'your', 'our', 'their', 'this', 'these', 'those'
        }
    
    def clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = ' '.join(text.split())
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text"""
        return self.clean_text(text).split()
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords"""
        return [t for t in tokens if t not in self.stop_words]
    
    def get_text_stats(self, text: str) -> Dict[str, Any]:
        """Get basic text statistics"""
        words = self.tokenize(text)
        return {
            "word_count": len(words),
            "char_count": len(text),
            "unique_words": len(set(words))
        }
    
    def preprocess_conversation(self, conversation: Dict) -> Dict:
        """Preprocess a single conversation"""
        processed_turns = []
        
        for turn in conversation['turns']:
            cleaned = self.clean_text(turn['text'])
            tokens = self.tokenize(cleaned)
            filtered = self.remove_stopwords(tokens)
            stats = self.get_text_stats(turn['text'])
            
            processed_turns.append({
                **turn,
                "cleaned_text": cleaned,
                "tokens": tokens,
                "filtered_tokens": filtered,
                "stats": stats
            })
        
        # Calculate conversation-level stats
        all_tokens = [t for turn in processed_turns for t in turn['filtered_tokens']]
        
        return {
            **conversation,
            "turns": processed_turns,
            "statistics": {
                "total_turns": len(processed_turns),
                "total_words": sum(turn['stats']['word_count'] for turn in processed_turns),
                "unique_words": len(set(all_tokens))
            }
        }
    
    def process_corpus(self, conversations: List[Dict]) -> List[Dict]:
        """Process entire corpus"""
        return [self.preprocess_conversation(conv) for conv in conversations]


class CorpusAnnotator:
    """Annotate corpus with intents and dialogue acts"""
    
    def __init__(self):
        # Intent classification patterns
        self.intent_patterns = {
            "greeting": r'\b(hi|hello|hey|greetings|good morning)\b',
            "farewell": r'\b(bye|goodbye|see you|take care|farewell)\b',
            "help": r'\b(help|assist|support)\b',
            "inquiry": r'\b(what|how|when|where|why|question|tell me)\b',
            "booking": r'\b(book|reservation|room|hotel|booking)\b',
            "complaint": r'\b(not working|broken|issue|problem)\b',
            "thanks": r'\b(thank|thanks|appreciate)\b'
        }
        
        # Dialogue act patterns
        self.dialogue_act_patterns = {
            "question": r'\?$',
            "greeting": r'^(hi|hello|hey|greetings)',
            "farewell": r'^(bye|goodbye|see you)',
            "statement": r'^[A-Z][^.?!]*[.!]$'
        }
    
    def annotate_intent(self, text: str) -> Dict[str, Any]:
        """Annotate intent using regex patterns"""
        text_lower = text.lower()
        
        # Check each pattern
        for intent, pattern in self.intent_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return {
                    "primary_intent": intent,
                    "confidence": 0.8,
                    "method": "pattern_matching"
                }
        
        # Default if no pattern matches
        return {
            "primary_intent": "other",
            "confidence": 0.3,
            "method": "default"
        }
    
    def annotate_dialogue_act(self, text: str) -> str:
        """Annotate dialogue act"""
        for act, pattern in self.dialogue_act_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return act
        return "statement"
    
    def extract_slots(self, text: str) -> List[Dict[str, str]]:
        """Extract simple slots from text"""
        slots = []
        text_lower = text.lower()
        
        # Simple slot extraction
        if "room" in text_lower or "hotel" in text_lower:
            slots.append({"slot_type": "accommodation", "value": "room"})
        if "price" in text_lower or "cost" in text_lower:
            slots.append({"slot_type": "price", "value": "inquiry"})
        if "order" in text_lower or "package" in text_lower:
            slots.append({"slot_type": "order", "value": "reference"})
        
        return slots
    
    def annotate_conversation(self, conversation: Dict) -> Dict:
        """Annotate entire conversation"""
        annotated_turns = []
        
        for turn in conversation['turns']:
            intent = self.annotate_intent(turn['text'])
            dialogue_act = self.annotate_dialogue_act(turn['text'])
            slots = self.extract_slots(turn['text'])
            
            annotated_turns.append({
                **turn,
                "annotations": {
                    "intent": intent,
                    "dialogue_act": dialogue_act,
                    "slots": slots
                }
            })
        
        return {
            **conversation,
            "turns": annotated_turns,
            "annotation_stats": {
                "total_annotations": len(annotated_turns),
                "annotator_version": "1.0"
            }
        }
    
    def annotate_corpus(self, conversations: List[Dict]) -> List[Dict]:
        """Annotate entire corpus"""
        return [self.annotate_conversation(conv) for conv in conversations]


class CorpusBuilder:
    """Build and manage the final corpus"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.annotations_dir = self.data_dir / "annotations"
        
        for d in [self.raw_dir, self.processed_dir, self.annotations_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def create_splits(self, conversations: List[Dict], 
                      train_ratio: float = 0.7,
                      val_ratio: float = 0.15) -> Dict[str, List[Dict]]:
        """Create train/val/test splits"""
        shuffled = conversations.copy()
        random.shuffle(shuffled)
        
        n = len(shuffled)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        
        return {
            "train": shuffled[:train_end],
            "val": shuffled[train_end:val_end],
            "test": shuffled[val_end:]
        }
    
    def generate_statistics(self, conversations: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive corpus statistics"""
        stats = {
            "total_conversations": len(conversations),
            "total_turns": 0,
            "total_words": 0,
            "domains": Counter(),
            "intents": Counter(),
            "dialogue_acts": Counter()
        }
        
        for conv in conversations:
            stats["domains"][conv.get("domain", "unknown")] += 1
            stats["total_turns"] += len(conv['turns'])
            
            for turn in conv['turns']:
                stats["total_words"] += turn.get('stats', {}).get('word_count', 0)
                
                if 'annotations' in turn:
                    intent = turn['annotations']['intent']['primary_intent']
                    stats["intents"][intent] += 1
                    
                    dialogue_act = turn['annotations']['dialogue_act']
                    stats["dialogue_acts"][dialogue_act] += 1
        
        return stats
    
    def save_corpus(self, conversations: List[Dict], name: str = "corpus"):
        """Save corpus in multiple formats"""
        
        # Save as JSON
        json_path = self.processed_dir / f"{name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=2, ensure_ascii=False)
        
        # Save as CSV (flattened)
        rows = []
        for conv in conversations:
            for turn in conv['turns']:
                row = {
                    "conversation_id": conv['conversation_id'],
                    "domain": conv.get('domain', ''),
                    "turn_id": turn['turn_id'],
                    "speaker": turn['speaker'],
                    "text": turn['text'],
                    "intent": turn.get('annotations', {}).get('intent', {}).get('primary_intent', ''),
                    "dialogue_act": turn.get('annotations', {}).get('dialogue_act', '')
                }
                rows.append(row)
        
        if rows:
            csv_path = self.processed_dir / f"{name}.csv"
            headers = list(rows[0].keys())
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write(','.join(headers) + '\n')
                for row in rows:
                    values = [str(row.get(h, '')).replace(',', ';') for h in headers]
                    f.write(','.join(values) + '\n')
        
        print(f"✓ Saved corpus to:\n  JSON: {json_path}\n  CSV: {csv_path}")
        return json_path


def run_pipeline(num_conversations: int = 50):
    """Run the complete corpus creation pipeline"""
    
    print("=" * 60)
    print("CONVERSATIONAL CORPUS PIPELINE")
    print("=" * 60)
    
    # Step 1: Data Collection
    print("\n[1/5] Collecting conversation data...")
    collector = CorpusDataCollector()
    raw_conversations = collector.generate_synthetic_conversations(num_conversations)
    collector.save_raw_data("data/raw/raw_conversations.json")
    print(f"  → Generated {len(raw_conversations)} conversations")
    
    # Step 2: Preprocessing
    print("\n[2/5] Preprocessing conversations...")
    preprocessor = CorpusPreprocessor()
    processed_conversations = preprocessor.process_corpus(raw_conversations)
    print(f"  → Preprocessed {len(processed_conversations)} conversations")
    
    # Step 3: Annotation
    print("\n[3/5] Annotating corpus...")
    annotator = CorpusAnnotator()
    annotated_conversations = annotator.annotate_corpus(processed_conversations)
    print(f"  → Annotated {len(annotated_conversations)} conversations")
    
    # Step 4: Build Corpus
    print("\n[4/5] Building final corpus...")
    builder = CorpusBuilder()
    splits = builder.create_splits(annotated_conversations)
    builder.save_corpus(annotated_conversations, "complete_corpus")
    
    # Save individual splits
    for split_name, split_data in splits.items():
        if split_data:
            builder.save_corpus(split_data, f"corpus_{split_name}")
    
    # Step 5: Generate Statistics
    print("\n[5/5] Generating statistics...")
    stats = builder.generate_statistics(annotated_conversations)
    
    # Display statistics
    print("\n" + "=" * 60)
    print("CORPUS STATISTICS")
    print("=" * 60)
    print(f"Total conversations: {stats['total_conversations']}")
    print(f"Total turns: {stats['total_turns']}")
    print(f"Total words: {stats['total_words']}")
    
    print("\nDomain Distribution:")
    for domain, count in stats['domains'].items():
        print(f"  {domain}: {count} ({count/stats['total_conversations']*100:.1f}%)")
    
    print("\nIntent Distribution:")
    for intent, count in stats['intents'].most_common(10):
        print(f"  {intent}: {count}")
    
    print("\nDialogue Act Distribution:")
    for act, count in stats['dialogue_acts'].most_common():
        print(f"  {act}: {count}")
    
    print("\n" + "=" * 60)
    print("✓ PIPELINE COMPLETE!")
    print("=" * 60)
    
    return annotated_conversations, stats


def explore_corpus():
    """Load and explore the created corpus"""
    corpus_path = "data/processed/complete_corpus.json"
    
    if not os.path.exists(corpus_path):
        print(f"Corpus not found at {corpus_path}. Run pipeline first.")
        return None
    
    with open(corpus_path, 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    
    print("\n" + "=" * 60)
    print("CORPUS EXPLORATION")
    print("=" * 60)
    
    if corpus:
        sample = corpus[0]
        print(f"\n📝 Sample Conversation: {sample['conversation_id']}")
        print(f"📂 Domain: {sample['domain']}")
        print(f"💬 Total turns: {sample['statistics']['total_turns']}")
        print("\n" + "─" * 50)
        
        for turn in sample['turns'][:8]:
            speaker_icon = "👤" if turn['speaker'] == 'user' else "🤖"
            print(f"\n{speaker_icon} [{turn['speaker'].upper()}]: {turn['text']}")
            if 'annotations' in turn:
                intent = turn['annotations']['intent']['primary_intent']
                act = turn['annotations']['dialogue_act']
                print(f"   🏷️  Intent: {intent} | 🎭 Act: {act}")
        
        if len(sample['turns']) > 8:
            print(f"\n   ... and {len(sample['turns']) - 8} more turns")
    else:
        print("No conversations found in corpus")
    
    return corpus


if __name__ == "__main__":
    # Run the complete pipeline
    corpus, stats = run_pipeline(num_conversations=50)
    
    # Explore the created corpus
    explore_corpus()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS")
    print("=" * 60)
    print("Your conversational corpus is ready! You can now:")
    print("  1. 📊 Load the corpus for training NLP models")
    print("  2. 📁 Use data/processed/complete_corpus.csv for analysis")
    print("  3. 🧠 Build intent classifiers with the annotated data")
    print("  4. 💬 Create dialogue systems using the conversation flows")
    print("\n📁 Files saved in:")
    print("   - data/raw/raw_conversations.json")
    print("   - data/processed/complete_corpus.json")
    print("   - data/processed/complete_corpus.csv")