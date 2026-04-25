import re
import nltk
import spacy
from typing import List, Dict, Any, Tuple
from collections import Counter
from textblob import TextBlob

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class ConversationPreprocessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
        
    def clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        return nltk.word_tokenize(text)
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from tokens"""
        return [token for token in tokens if token not in self.stop_words]
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """Lemmatize tokens using spaCy"""
        text = ' '.join(tokens)
        doc = self.nlp(text)
        return [token.lemma_ for token in doc]
    
    def extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """Extract named entities using spaCy"""
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]
    
    def get_sentiment(self, text: str) -> Dict[str, float]:
        """Get sentiment polarity and subjectivity"""
        blob = TextBlob(text)
        return {
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity
        }
    
    def compute_turn_statistics(self, conversation: Dict) -> Dict:
        """Compute statistics for conversation turns"""
        turns = conversation['turns']
        turn_lengths = [len(turn['text'].split()) for turn in turns]
        
        return {
            "avg_turn_length": sum(turn_lengths) / len(turn_lengths),
            "max_turn_length": max(turn_lengths),
            "min_turn_length": min(turn_lengths),
            "total_turns": len(turns)
        }
    
    def preprocess_conversation(self, conversation: Dict) -> Dict:
        """Full preprocessing pipeline for a conversation"""
        processed_turns = []
        
        for turn in conversation['turns']:
            # Clean text
            cleaned_text = self.clean_text(turn['text'])
            # Tokenize
            tokens = self.tokenize(cleaned_text)
            # Remove stopwords
            filtered_tokens = self.remove_stopwords(tokens)
            # Lemmatize
            lemmas = self.lemmatize(filtered_tokens)
            # Extract entities
            entities = self.extract_entities(turn['text'])
            # Get sentiment
            sentiment = self.get_sentiment(turn['text'])
            
            processed_turns.append({
                **turn,
                "original_text": turn['text'],
                "cleaned_text": cleaned_text,
                "tokens": tokens,
                "filtered_tokens": filtered_tokens,
                "lemmas": lemmas,
                "entities": entities,
                "sentiment": sentiment
            })
        
        processed_conversation = {
            **conversation,
            "turns": processed_turns,
            "statistics": self.compute_turn_statistics(conversation)
        }
        
        return processed_conversation
    
    def process_corpus(self, conversations: List[Dict]) -> List[Dict]:
        """Process entire corpus"""
        processed = []
        for conv in conversations:
            processed.append(self.preprocess_conversation(conv))
        return processed

if __name__ == "__main__":
    preprocessor = ConversationPreprocessor()
    sample_text = "Hello! I need help with my product. It's not working properly."
    print(f"Cleaned: {preprocessor.clean_text(sample_text)}")
    print(f"Entities: {preprocessor.extract_entities(sample_text)}")
    print(f"Sentiment: {preprocessor.get_sentiment(sample_text)}")