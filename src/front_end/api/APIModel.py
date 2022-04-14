"""
  MUKALMA - A Knowledge-Powered Conversational Agent
  Project Id: F21-20-R-KBCAgent

  APIModel Class
    - Provides the configuration settings to be used for the pipeline model
    - This allows the API Model to be highly configurable and interchangeable
"""

# Imports
from ...models.mukalma.mukalma import MUKALMA


# Class Definition
class APIModel:
    def __init__(self, source):
        self.params = {
            "source": source,
            "flavors": {
                "small": {
                    "dialoGPT": "../../../models/DialoGPT-small",
                    "t5": "../../../models/t5-small",
                    "bert": "../../../models/bert-base-cased-squad2",
                    "miniLM": "../../../models/all-MiniLM-L6-v2",
                    "t5-e2e": "../../../models/t5-small-e2e-qg",
                    "intent": "../../../models/intent.sav",
                    "mpnet": "../../../models/all-mpnet-base-v2"
                },
                "medium": {
                    "dialoGPT": "../../../models/DialoGPT-medium",
                    "t5": "../../../models/t5-base",
                    "bert": "../../../models/bert-base-cased-squad2",
                    "miniLM": "../../../models/all-MiniLM-L6-v2",
                    "t5-e2e": "../../../models/t5-base-e2e-qg",
                    "intent": "../../../models/intent.sav",
                    "mpnet": "../../../models/all-mpnet-base-v2"
                },
                "large": {
                    "dialoGPT": "../../../models/DialoGPT-medium",
                    "t5": "../../../models/t5-large",
                    "bert": "../../../models/bert-base-cased-squad2",
                    "miniLM": "../../../models/all-MiniLM-L6-v2",
                    "t5-e2e": "../../../models/t5-base-e2e-qg",
                    "intent": "../../../models/intent.sav",
                    "mpnet": "../../../models/all-mpnet-base-v2"
                },
                "x-large": {
                    "dialoGPT": "../../../models/DialoGPT-large",
                    "t5": "../../../models/t5-large",
                    "bert": "../../../models/bert-base-cased-squad2",
                    "miniLM": "../../../models/all-MiniLM-L6-v2",
                    "t5-e2e": "../../../models/t5-base-e2e-qg",
                    "intent": "../../../models/intent.sav",
                    "mpnet": "../../../models/all-mpnet-base-v2"
                }
            },
            "selected_flavor": "large",
            "use_cuda": {
                "dialoGPT": True,
                "t5": False,
                "t5-e2e": True,
                "miniLM": False,
                "mpnet": False
            }
        }
        self.model = MUKALMA(self.params)

    def updateKnowledge(self, knowledge):
        self.model.set_knowledge_source(knowledge)

    def reply(self, message):
        return self.model.get_response(message)

    def exit(self):
        self.model.exit()
