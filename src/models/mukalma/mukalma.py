"""
  MUKALMA - A Knowledge-Powered Conversational Agent
  Project Id: F21-20-R-KBCAgent

  MUKALMA Class
    - Primary pipeline class for MUKALMA, as developed in Iteration 1 and 2 of the project
    - Defines a model that makes use of an ensemble Knowledge-Retrieval module
    - In conjunction with a Language Model for dialog generation.
    - This model should be used for generating human-like dialog grounded on knowledge.
"""


# Importing Models
from ...util_models.DialoGPTController import DialoGPTController
from src.util_models.T5.T5ClozeController import T5ClozeController, getMaskToken
from ...util_models.SentenceModel import SentenceModel
from ...util_models.T5.T5ForQuestionGeneration import T5ForQuestionGeneration
from ...util_models.FlairPOSTagger import FlairPOSTagger

# Importing NLU Components
from .nlu.partsOfSpeech import get_nouns, match_questions, truecasing_by_pos, fix_sentence
from .nlu.intentRecognition import IntentRecognizer

from .KnowledgeSource import KnowledgeSource

from torch import cuda


class MUKALMA:
    def __init__(self, params):
        self.TAG = 'MUKALMA'

        # Check for Nvidia CUDA Support on the machine
        cuda.empty_cache()
        print(f"{self.TAG}: CUDA GPU is {'not' if not cuda.is_available() else ''} available on this machine")

        # Parameter Configurations
        self.flavor_selected = params["selected_flavor"]
        self.flavor_config = params["flavors"][self.flavor_selected]
        self.model_flavors = params["flavors"]
        self.cuda_use = params["use_cuda"]

        self.sentence_model = SentenceModel(self.flavor_config["miniLM"], use_cuda=self.cuda_use["miniLM"])
        
        self.intentRecognizer = IntentRecognizer(model_path=self.flavor_config["intent"])

        self.dialogue_model = DialoGPTController(self.flavor_config["dialoGPT"], use_cuda=self.cuda_use["dialoGPT"])
        self.dialogue_model.initialize_model(refresh=True)

        self.question_generation_model = T5ForQuestionGeneration(self.flavor_config["t5-e2e"],
                                                                 use_cuda=self.cuda_use["t5-e2e"])
        self.question_generation_model.initialize_model()

        self.cloze_model = T5ClozeController(self.flavor_config["t5"], use_cuda=self.cuda_use["t5"], num_responses=3)
        self.cloze_model.initialize_model()

        self.tagger = FlairPOSTagger('flair/pos-english-fast')

        # Initialize Knowledge Source using the Sentence Embedding Model of choice
        self.knowledge_db = KnowledgeSource(self.sentence_model.model)

        # Keeps track of the topic that is currently being talked about
        self.topic_str = ""

    def set_knowledge_source(self, knowledge_source):
        pass

    def __extract_topic(self, message):
        pos_list = self.tagger.get_pos_tags(message)
        pos_words = []
        prev_type = None
        for pos in pos_list:
            # If the current part of speech isn't a Noun, reset the previous type and skip this
            if pos[1][:2] not in ['NN', 'CD']:
                prev_type = None
                continue

            # If the current pos is relevant, process it
            # If the previous pos had the same type, it might be a compound word, append it
            # If not, just append it to the list of relevant pos words
            if pos[1] == prev_type:
                pos_words[-1] = f"{pos_words[-1]} {pos[0]}"
            else:
                pos_words.append(pos[0])

        return pos_words

    def get_best_response_id(self, responses, log_responses=False, prefix=""):
        max_length = -1
        max_id = 0
        for response_id, response in enumerate(responses):
            if log_responses:
                print(f"[{self.TAG}: {prefix} {response_id}]: {response} .")
            if len(response) > max_length:
                max_length = len(response)
                max_id = response_id

        return max_id

    def generate_knowledge_based_response(self, message, knowledge_sent, extracted_question=""):
        message = fix_sentence(message)

        # If a relevant knowledge sentence couldn't be found, return the best response the dialogue model could generate
        if knowledge_sent == "":
            responses = self.dialogue_model.predict(message, output_fragment=knowledge_sent)
            return responses[self.get_best_response_id(responses)], responses

        # Take the word / phrase retrieved from the knowledge source and complete it
        # This is done by framing this task as a Cloze task
        cloze_responses = self.cloze_model.generate_cloze_responses(
            f"{message} {getMaskToken(0)} {knowledge_sent} {getMaskToken(1)} .".lower()
        )

        fragmented_outputs = []
        outputs = []
        for cloze_response in cloze_responses:
            # Take the the output with the 'blanks' filled. Take a slice of the output by removing the input prompt
            # from it. Use a dialogue model to complete this output slice, in an attempt to make the reply open ended
            knowledge_sent = cloze_response[len(message) + 1:-2] + "."

            # We use two methods to generate the output. One sentence is a knowledge-grounded response. The second,
            # following sentence is a dialog-style response which follows from the first generated sentence
            # We need to keep track of this separation between the two sentences
            fragmented_output = [(knowledge_sent, dialog)
                                 for dialog in self.dialogue_model.predict(message, output_fragment=knowledge_sent)]
            output = [kg + dg for (kg, dg) in fragmented_output]

            fragmented_outputs.extend(fragmented_output)
            outputs.extend(output)

            print(f"OUTPUTS: \n{fragmented_output}")

        # Obtain the index of the best response, and lookup the best response string (complete and fragmented on the
        # basis of the method used to generate the string)
        best_response_id = self.get_best_response_id(outputs)
        best_fragmented_response = fragmented_outputs[best_response_id]
        best_response = outputs[best_response_id]

        # Check if the answer generated by the dialog model 'follows from' the generated knowledge-grounded output
        # at index 0 of the fragmented response
        """
        self.cloze_model.check_equivalence(
            best_fragmented_response[1], f"{self.knowledge_source}. {extracted_question} {best_fragmented_response[0]}"
        )
        """

        # Swap the best response to index 0 to indicate that this was the selected response
        outputs[best_response_id] = outputs[0]
        outputs[0] = best_response

        return best_response, outputs
    # End of function

    def find_relevant_response(self, message, cur_turn_knowledge, cur_turn_knowledge_tok):
        selected_question = message

        # Matching Nouns
        """
        if match_nouns_from_set(message, self.knowledge_source_pos) == 0:
            return selected_question, "", -1, -1
        """
        
        # Intent Recognition
        intent = self.intentRecognizer.recognizeIntent(message)
        print(f"[{self.TAG}]: Intent: {intent}")
        knowledge_sent, knowledge_start_index, knowledge_end_index = "", -1, -1

        # Setting the question from the either the message (if the message was a question)
        # Or generate a question from the statement
        if intent == "Statement":
            knowledge_questions = self.question_generation_model.generate_questions(message, "")
            knowledge_question = knowledge_questions[0] if len(knowledge_questions) > 0 else None
        else:
            knowledge_question = message

        # Fetching answer from T5
        if knowledge_question is not None:
            print(f"[{self.TAG}]: [Message-Question]: {knowledge_question}")
            selected_question = knowledge_question
            knowledge_sent, knowledge_start_index, knowledge_end_index = \
                self.cloze_model.get_answers(message, cur_turn_knowledge)
            print(f"[{self.TAG}]: [CLOZE-Based]: Knowledge sent: {knowledge_sent}")

        # If a knowledge_sent couldn't be found, find the most similar sentence instead
        if len(knowledge_sent) == 0:
            print(f"[{self.TAG}]: SENT TOK KNOWLEDGE: { cur_turn_knowledge_tok }")
            print(f"\n\nSENT TOK KNOWLEDGE:\n{cur_turn_knowledge_tok[:4]}\n\nmessage:\n{message}")
            knowledge_sents, knowledge_start_index, knowledge_end_index = \
                self.sentence_model.get_most_similar_sentence(message, cur_turn_knowledge_tok), -1, -1

            if len(knowledge_sents) != 0:
                # Pick the best matched sentence
                # TODO: An additional layer of scoring can be added before selecting from the set of best matched sentences
                knowledge_sent = knowledge_sents[0]
                # Generate a question from the message and the similar sentence
                knowledge_questions = []
                message_nouns = get_nouns(message)

                print(f"[{self.TAG}]: Using the message nouns: {message_nouns}")

                # Finding all the questions for each noun we identify in the message
                message_keyword = " ".join(message_nouns)
                knowledge_questions.extend(self.question_generation_model.generate_questions(knowledge_sent, message_keyword))
                print(f"[{self.TAG}]: Questions Generated: {knowledge_questions}")

                # Select the most relevant question from the list of generated questions
                # based on basic word matching
                selected_questions = match_questions(message, knowledge_questions, knowledge_sent)

                # Obtain the knowledge span by querying the source using a QA model and the best question
                if len(selected_questions) != 0:
                    selected_question = selected_questions[0]
                    print(f"[{self.TAG}]: Using the question: {selected_question}")

                    knowledge_sent, knowledge_start_index, knowledge_end_index = \
                        self.cloze_model.get_answers(selected_question, knowledge_sent)
                else:
                    knowledge_sent, knowledge_start_index, knowledge_end_index = "", -1, -1
                    selected_question = message
                # End else
            else:
                selected_question = message
            # End if
        # End if

        # Logging and Return
        print(f"[{self.TAG}]: Response: {knowledge_sent} start span: {knowledge_start_index} end span: {knowledge_end_index}")
        return selected_question, knowledge_sent, knowledge_start_index, knowledge_end_index

    def get_response(self, message):
        # Get a list of topics that may have been mentioned in the message
        topics = self.__extract_topic(message)

        print(f"TOPIC SEARCH STRING: {topics}")

        # If the message talks about a new topic...
        # Request Knowledge DB to fetch data relevant to the current message, update the db
        # and finally, return the most relevant document for this message
        cur_turn_knowledge, cur_turn_knowledge_tok = "", []
        if len(topics) != "":
            cur_turn_knowledge_tok = self.knowledge_db.fetch_topic_data(topics, message)
            cur_turn_knowledge = ' '.join(cur_turn_knowledge_tok)

        # Retrieve the relevant knowledge sentence from the knowledge source
        selected_question, knowledge_sent, knowledge_start_index, knowledge_end_index = "", "", 0, 0
        if len(cur_turn_knowledge_tok) != 0:
            selected_question, knowledge_sent, knowledge_start_index, knowledge_end_index = self.find_relevant_response(
                message, cur_turn_knowledge, cur_turn_knowledge_tok)

        # Condition on the knowledge sentence, and generate knowledge-grounded dialog
        best_response, knowledge_grounded_responses = \
            self.generate_knowledge_based_response(message, knowledge_sent)

        # Cleaning the responses
        best_response = truecasing_by_pos(best_response)
        for i in range(len(knowledge_grounded_responses)):
            knowledge_grounded_responses[i] = truecasing_by_pos(knowledge_grounded_responses[i])

        # Logging and Return
        print(f"[{self.TAG}]: GENERATED RESPONSE: {knowledge_grounded_responses}")
        return {"knowledge_sent": knowledge_sent,
                "response": best_response, "candidates": knowledge_grounded_responses,
                "k_start_index": knowledge_start_index, "k_end_index": knowledge_end_index}
