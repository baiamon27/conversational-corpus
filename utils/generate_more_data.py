# generate_more_data.py
from complete_corpus import CorpusDataCollector

collector = CorpusDataCollector()
more_conversations = collector.generate_synthetic_conversations(200)
collector.save_raw_data("data/raw/more_conversations.json")