import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from data_collector import DataCollector
from preprocessor import ConversationPreprocessor
from annotator import CorpusAnnotator
from corpus_builder import CorpusBuilder

def run_full_pipeline(num_conversations: int = 100):
    """Run complete corpus creation pipeline"""
    
    print("=" * 50)
    print("CONVERSATIONAL CORPUS PIPELINE")
    print("=" * 50)
    
    # Step 1: Data Collection
    print("\n[1/5] Collecting conversation data...")
    collector = DataCollector()
    conversations = collector.generate_synthetic_conversations(num_conversations)
    collector.save_raw_data("data/raw/raw_conversations.json")
    print(f"✓ Collected {len(conversations)} conversations")
    
    # Step 2: Preprocessing
    print("\n[2/5] Preprocessing conversations...")
    preprocessor = ConversationPreprocessor()
    processed_conversations = preprocessor.process_corpus(conversations)
    print(f"✓ Preprocessed {len(processed_conversations)} conversations")
    
    # Step 3: Annotation
    print("\n[3/5] Annotating corpus...")
    annotator = CorpusAnnotator()
    annotated_conversations = []
    for conv in processed_conversations:
        annotated_conversations.append(annotator.annotate_conversation(conv))
    print(f"✓ Annotated {len(annotated_conversations)} conversations")
    
    # Step 4: Build Corpus
    print("\n[4/5] Building final corpus...")
    builder = CorpusBuilder()
    splits = builder.create_dataset_splits(annotated_conversations)
    builder.save_corpus(annotated_conversations, "complete_corpus")
    
    # Save splits
    for split_name, split_data in splits.items():
        builder.save_corpus(split_data, f"corpus_{split_name}")
    
    # Step 5: Generate Statistics
    print("\n[5/5] Generating statistics...")
    stats = builder.generate_statistics(annotated_conversations)
    
    print("\n" + "=" * 50)
    print("CORPUS STATISTICS")
    print("=" * 50)
    print(f"Total conversations: {stats['total_conversations']}")
    print(f"Total turns: {stats['total_turns']}")
    print(f"Avg turns/conversation: {stats['avg_turns_per_conversation']:.2f}")
    
    print("\nIntent Distribution:")
    for intent, count in stats['intent_distribution'].most_common(5):
        print(f"  {intent}: {count}")
    
    print("\nDialogue Act Distribution:")
    for act, count in stats['dialogue_act_distribution'].most_common(5):
        print(f"  {act}: {count}")
    
    print("\nTopic Distribution:")
    for topic, count in stats['topic_distribution'].items():
        print(f"  {topic}: {count}")
    
    # Create datasets for downstream tasks
    print("\n" + "=" * 50)
    print("DOWNSTREAM DATASETS")
    print("=" * 50)
    
    intent_df = builder.create_intent_dataset(annotated_conversations)
    print(f"Intent classification dataset: {len(intent_df)} samples")
    intent_df.head().to_csv("data/processed/intent_dataset_sample.csv")
    
    dialogue_act_df = builder.create_dialogue_act_dataset(annotated_conversations)
    print(f"Dialogue act dataset: {len(dialogue_act_df)} samples")
    dialogue_act_df.head().to_csv("data/processed/dialogue_act_dataset_sample.csv")
    
    slot_df = builder.create_slot_filling_dataset(annotated_conversations)
    print(f"Slot filling dataset: {len(slot_df)} samples")
    
    print("\n✓ Pipeline complete!")
    print("\nOutput files saved in 'data/processed/' directory")
    
    return annotated_conversations, stats

def load_and_explore():
    """Load and explore the created corpus"""
    builder = CorpusBuilder()
    corpus_path = builder.processed_dir / "complete_corpus.json"
    
    if corpus_path.exists():
        with open(corpus_path, 'r') as f:
            corpus = json.load(f)
        
        print("\n" + "=" * 50)
        print("CORPUS EXPLORATION")
        print("=" * 50)
        
        # Show sample conversation
        sample_conv = corpus[0]
        print(f"\nSample Conversation: {sample_conv['conversation_id']}")
        print(f"Topic: {sample_conv['topic']}")
        print("\nTurns:")
        for turn in sample_conv['turns'][:5]:  # First 5 turns
            print(f"  [{turn['speaker']}]: {turn['text']}")
            if 'annotations' in turn:
                print(f"    Intent: {turn['annotations']['intent']['primary_intent']}")
                print(f"    Dialogue Act: {turn['annotations']['dialogue_act']}")
        
        return corpus
    else:
        print("Corpus not found. Run the pipeline first.")
        return None

if __name__ == "__main__":
    # Run the complete pipeline
    corpus, stats = run_full_pipeline(num_conversations=100)
    
    # Explore the created corpus
    load_and_explore()