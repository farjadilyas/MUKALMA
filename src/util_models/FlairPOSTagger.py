"""
  MUKALMA - A Knowledge-Powered Conversational Agent
  Project Id: F21-20-R-KBCAgent

  Wrapper class for the Flair POS tagger - one of the top ranked POS taggers across multiple metrics

  @Author: Muhammad Farjad Ilyas
  @Date: 29th March 2022
"""

from rich.console import Console
from pathlib import Path

# Flair imports for POS tagging
import flair
from flair.data import Sentence
from flair.models import SequenceTagger

# Change the cache directory for Flair models to one within this project's model directory
flair.cache_root = Path("../../../models/.flair")
console = Console(record=True)


class FlairPOSTagger:
    def __init__(self, model_path='flair/pos-english-fast'):
        self.TAG = 'FlairPOSTagger'

        console.log(f"""[{self.TAG}]: Loading {model_path}...\n""")
        self.model = SequenceTagger.load(model_path)

    def get_pos_tags(self, message):
        sentence = Sentence(message)
        self.model.predict(sentence)
        toks = sentence.tokens
        tags = []
        for idx, entity in enumerate(sentence.get_spans('pos')):
            tags.append((toks[idx].text, entity.get_labels()[0].value))
        return tags

    def get_tags(self, message):
        sentence = Sentence(message)
        self.model.predict(message)
        toks = sentence.tokens

        # POS
        pos_tags = []
        for idx, entity in enumerate(sentence.get_spans('pos')):
            pos_tags.append((toks[idx].text, entity.get_labels()[0].value))

        # NER
        ner_tags = []
        for idx, entity in enumerate(sentence.get_spans('ner')):
            pos_tags.append((toks[idx].text, entity.get_labels()[0].value))

        return pos_tags, ner_tags
