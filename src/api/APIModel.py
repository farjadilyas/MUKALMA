"""
  MUKALMA - A Knowledge-Powered Conversational Agent
  Project Id: F21-20-R-KBCAgent

  APIModel Class
    - Provides the configuration settings to be used for the pipeline model
    - This allows the API Model to be highly configurable and interchangeable
"""

# Imports
from ..mukalma.mukalma import MUKALMA
from concurrent.futures import ThreadPoolExecutor


# Class Definition
class APIModel:
    def __init__(self, progress_update_queue):
        self.executor = ThreadPoolExecutor(1)
        self.params = {
            "flavors": {
                "small": {
                    "dialoGPT": "../../models/DialoGPT-small",
                    "t5": "../../models/t5-small",
                    "bert": "../../models/bert-base-cased-squad2",
                    "miniLM": "../../models/all-MiniLM-L6-v2",
                    "t5-e2e": "../../models/t5-small-e2e-qg",
                    "intent": "../../models/intent.sav",
                    "mpnet": "../../models/all-mpnet-base-v2"
                },
                "medium": {
                    "dialoGPT": "../../models/DialoGPT-medium",
                    "t5": "../../models/t5-base",
                    "bert": "../../models/bert-base-cased-squad2",
                    "miniLM": "../../models/all-MiniLM-L6-v2",
                    "t5-e2e": "../../models/t5-base-e2e-qg",
                    "intent": "../../models/intent.sav",
                    "mpnet": "../../models/all-mpnet-base-v2"
                },
                "large": {
                    "dialoGPT": "../../models/DialoGPT-medium",
                    "t5": "../../models/t5-large",
                    "bert": "../../models/bert-base-cased-squad2",
                    "miniLM": "../../models/all-MiniLM-L6-v2",
                    "t5-e2e": "../../models/t5-base-e2e-qg",
                    "intent": "../../models/intent.sav",
                    "mpnet": "../../models/all-mpnet-base-v2"
                },
                "x-large": {
                    "dialoGPT": "../../models/DialoGPT-large",
                    "t5": "../../models/t5-large",
                    "bert": "../../models/bert-base-cased-squad2",
                    "miniLM": "../../models/all-MiniLM-L6-v2",
                    "t5-e2e": "../../models/t5-base-e2e-qg",
                    "intent": "../../models/intent.sav",
                    "mpnet": "../../models/all-mpnet-base-v2"
                }
            },
            "selected_flavor": "large",
            "use_cuda": {
                "dialoGPT": True,
                "t5": False,
                "t5-e2e": False,
                "miniLM": True,
                "mpnet": True
            },
            "dialog_exclusion_list": "../../res/dialog_word_exclusion_list.txt",
            "offline": False
        }
        self.model = MUKALMA(self.params, progress_update_queue)
        
    def reply(self, message):
        self.executor.submit(self.model.get_response, message)
        return {}

    def exit(self):
        self.model.exit()

    def clear_context(self):
        self.model.clear_context()

    def set_topic(self, topic):
        self.model.set_topic([topic])
