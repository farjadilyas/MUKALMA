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
from ...util_models.TopicTransitionModel import TopicTransitionModel

# Importing NLU Components
from .nlu.partsOfSpeech import get_nouns, match_questions, fix_sentence
from .nlu.intentRecognition import IntentRecognizer

# Import packages for text preprocessing of messages
from nltk.tokenize import word_tokenize
from .nlu.svo_utils import extract_named_entities, get_lemmatizer
import dateparser as dp
from word2number import w2n
import re
from time import localtime, strftime

from .KnowledgeSource import KnowledgeSource

from torch import cuda


def clean_answer(s):
    """
      Replace brackets in answers with commas containing the same text
    """

    # Match an opening bracket and its preceding character, or a closing bracket and its following character
    splits = re.split(r'(.?\(|\).?)', s)
    cleaned_ans = ""

    # If the split encountered is an opening bracket, introduce a comma before appending its preceding character
    # append the following character after the comma if the split is a closing bracket
    # If the split is not a bracket, append the entire split to the cleaned answer
    # This has the effect of replacing brackets with commas
    for split in splits:
        if len(split) >= 2 and split[1] == '(':
            cleaned_ans = f"{cleaned_ans},{split[0]}"
        elif len(split) >= 2 and split[0] == ')':
            cleaned_ans = f"{cleaned_ans},{split[1]}"
        else:
            cleaned_ans = f"{cleaned_ans}{split}"

    # Replace a range in the form of number - number to the form number to number
    cleaned_ans = re.sub(r'([0-9]+[^ ]*) ?- ?([0-9]+)', r'\1 to \2', cleaned_ans)

    return cleaned_ans


def word_to_num(word):
    try:
        return w2n.word_to_num(word)
    except ValueError:
        return None


# Define keywords used for text processing of strings that contain references to time
days_of_week = ['saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'friday']
future_words = ['next', 'later', 'future']
past_words = ['ago', 'past', 'previous', 'last']
range_words = ['past', 'last', 'next', 'within']
cur_year = int(strftime("%Y", localtime()))


def clean_input(s):
    lemmatizer = get_lemmatizer()
    p_msg = msg = s
    nes = extract_named_entities(msg)

    # Replace the named entities referring to dates in the input with date ranges, keep cleaned output in p_msg
    for ne in nes:
        if ne[1] != 'DATE':
            continue

        past = period = unit = None
        replace = None
        prev_proc_w = None
        year_range = False

        # Attempt to parse the named entity tagged as DATE
        try:
            dt = dp.parse(ne[0])
        except:
            dt = None
        if dt is not None:
            replace = str(dt.year)
        else:
            # Tokenize and iterate over the words making up the date named entity
            # This loop aims to extract whether the named entity is talking about the past/present/future
            # It also extracts the unit of time, and the amount of time mentioned in the named entity
            words = word_tokenize(ne[0])
            for w_id, word in enumerate(words):
                # Normalize words
                proc_w = lemmatizer.lemmatize(re.sub("'s", '', word.lower()))

                # Compare the normalized word against a set of lists to extract information
                if proc_w in range_words:
                    year_range = True
                if proc_w in days_of_week or proc_w == 'month':
                    replace = cur_year
                elif proc_w in past_words:
                    past = True
                elif proc_w in future_words:
                    past = False
                elif proc_w == 'this':
                    past = None
                elif proc_w == 'century':
                    unit = 100
                    if prev_proc_w is not None:
                        period = word_to_num(prev_proc_w)
                elif proc_w == 'decade':
                    unit = 10
                    if prev_proc_w is not None:
                        period = word_to_num(prev_proc_w)
                elif proc_w == 'year':
                    if prev_proc_w is not None:
                        period = word_to_num(prev_proc_w)
                    unit = 1
                prev_proc_w = proc_w

        # Prefix differs based on whether a specific time is mentioned, or if a range is mentioned
        prefix = "in "

        # Combine the information extracted from this named entity
        if past is None:
            replace = str(cur_year)
        if replace is not None:
            break
        if period is None:
            period = 1
        if past is not None and period is not None and unit is not None:
            replace = str(2022 + (-1 if past else 1) * period * unit)

        # Change prefix and replacement text if a range of time is mentioned instead of a specific year
        if replace is not None and year_range:
            prefix = "between "
            replace = f"{replace} - {cur_year}" if int(replace) < cur_year else f"{cur_year} - {replace}"

        # Replace the named entity in the message (p_msg) with the replacement text sent as the second parameter
        p_msg = re.sub(ne[0], prefix + replace, p_msg)

    return p_msg


class MUKALMA:
    def __init__(self, params, progress_update_queue):
        self.TAG = 'MUKALMA'
        self.progress_update_queue = progress_update_queue

        # Check for Nvidia CUDA Support on the machine
        cuda.empty_cache()
        print(
            f"[{self.TAG}]: __init___: CUDA GPU is {'not' if not cuda.is_available() else ''} available on this machine")

        # Parameter Configurations
        self.flavor_selected = params["selected_flavor"]
        self.flavor_config = params["flavors"][self.flavor_selected]
        self.model_flavors = params["flavors"]
        self.cuda_use = params["use_cuda"]

        # ------------------------------------------------------------------------------------------------------------
        # Loading Models

        self.sentence_model = SentenceModel(self.flavor_config["mpnet"], use_cuda=self.cuda_use["mpnet"])
        self.fast_sentence_model = SentenceModel(self.flavor_config["miniLM"], use_cuda=self.cuda_use["miniLM"])

        self.intentRecognizer = IntentRecognizer(model_path=self.flavor_config["intent"])

        self.dialogue_model = DialoGPTController(self.flavor_config["dialoGPT"], use_cuda=self.cuda_use["dialoGPT"])
        self.dialogue_model.initialize_model(refresh=True)

        self.question_generation_model = T5ForQuestionGeneration(self.flavor_config["t5-e2e"],
                                                                 use_cuda=self.cuda_use["t5-e2e"])
        self.question_generation_model.initialize_model()

        self.cloze_model = T5ClozeController(self.flavor_config["t5"], use_cuda=self.cuda_use["t5"], num_responses=3)
        self.cloze_model.initialize_model()

        self.tagger = FlairPOSTagger('flair/pos-english-fast')

        # Initialize Knowledge Source & Topic Transition Model using the Sentence Embedding Model of choice
        self.knowledge_db = KnowledgeSource(model=self.sentence_model.model, num_results=1, persist=True,
                                            persist_path='../../../res/knowledge_presets', use_hot_cache=True)

        # Responsible for tracking changes in the topic the conversation is centered around
        self.topic_transition_model = TopicTransitionModel(self.fast_sentence_model.model,
                                                           use_cuda=self.cuda_use["miniLM"])

        # ------------------------------------------------------------------------------------------------------------

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
                print(f"[{self.TAG}]: get_best_response_id: {prefix} {response_id}]: {response} .")
            if len(response) > max_length:
                max_length = len(response)
                max_id = response_id

        return max_id

    def generate_knowledge_based_response(self, message, knowledge_sent):
        message = fix_sentence(message)

        # If a relevant knowledge sentence couldn't be found, return the best response the dialogue model could generate
        if knowledge_sent == "":
            responses = self.dialogue_model.predict(message, output_fragment=knowledge_sent)
            self.progress_update_queue.put_nowait({"id": 2, "message": "Knowledge source could not be found",
                                                   "success": False})
            return responses[self.get_best_response_id(responses)], responses

        # Take the word / phrase retrieved from the knowledge source and complete it
        # This is done by framing this task as a Cloze task
        cloze_responses = self.cloze_model.generate_cloze_responses(
            f"{message} {getMaskToken(0)} {knowledge_sent} {getMaskToken(1)} ."
        )

        self.progress_update_queue.put_nowait({"id": 2, "message": "Cloze completion complete", "success": True})

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

            print(f"[{self.TAG}]: generate_knowledge_based_response: OUTPUTS: \n{fragmented_output}")

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
        print(f"[{self.TAG}]: find_relevant_response: Intent: {intent}")
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
            print(f"[{self.TAG}]: find_relevant_response: [Message-Question]: {knowledge_question}")
            selected_question = knowledge_question
            knowledge_sent, knowledge_start_index, knowledge_end_index = \
                self.cloze_model.get_answers(message, cur_turn_knowledge)
            print(f"[{self.TAG}]: find_relevant_response: [CLOZE-Based]: Knowledge sent: {knowledge_sent}")

        # If a knowledge_sent couldn't be found, find the most similar sentence instead
        if len(knowledge_sent) == 0:

            print(f"[{self.TAG}]: find_relevant_response: SENT TOK KNOWLEDGE: {cur_turn_knowledge_tok}")
            print(f"\n\n[{self.TAG}]: find_relevant_response: SENT TOK KNOWLEDGE:\n{cur_turn_knowledge_tok[:4]}\n\n")
            print("[{self.TAG}]: find_relevant_response: message:\n{message}")

            knowledge_sents, knowledge_start_index, knowledge_end_index = \
                self.sentence_model.get_most_similar_sentence(message, cur_turn_knowledge_tok), -1, -1

            if len(knowledge_sents) != 0:
                # Pick the best matched sentence
                # TODO: An additional layer of scoring can be added before selecting from the set of best matched sentences
                knowledge_sent = knowledge_sents[0]
                # Generate a question from the message and the similar sentence
                knowledge_questions = []
                message_nouns = get_nouns(message)

                print(f"[{self.TAG}]: find_relevant_response: Using the message nouns: {message_nouns}")

                # Finding all the questions for each noun we identify in the message
                message_keyword = " ".join(message_nouns)
                knowledge_questions.extend(
                    self.question_generation_model.generate_questions(knowledge_sent, message_keyword))
                print(f"[{self.TAG}]: find_relevant_response: Questions Generated: {knowledge_questions}")

                # Select the most relevant question from the list of generated questions
                # based on basic word matching
                selected_questions = match_questions(message, knowledge_questions, knowledge_sent)

                # Obtain the knowledge span by querying the source using a QA model and the best question
                if len(selected_questions) != 0:
                    selected_question = selected_questions[0]
                    print(f"[{self.TAG}]: find_relevant_response: Using the question: {selected_question}")

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
        print(
            f"[{self.TAG}]: find_relevant_response: Response: {knowledge_sent} start span: {knowledge_start_index} end span: {knowledge_end_index}")
        return selected_question, knowledge_sent, knowledge_start_index, knowledge_end_index

    def get_response(self, message):
        message = clean_input(message)

        # Get a list of topics that may have been mentioned in the message
        # Add keywords from conversation history if they're relevant, and update the topic transition model
        topics = self.topic_transition_model.update_topic(message, self.__extract_topic(message))

        print(f"[{self.TAG}]: get_response: MESSAGE KEYWORDS: {topics}")

        # If the message talks about a new topic...
        # Request Knowledge DB to fetch data relevant to the current message, update the db
        # and finally, return the most relevant document for this message
        knowledge_article, cur_turn_knowledge, cur_turn_knowledge_tok = "", "", []
        if len(topics) != 0:
            cur_turn_knowledge_tok, knowledge_article = self.knowledge_db.fetch_topic_data(topics, message)
            cur_turn_knowledge = ' '.join(cur_turn_knowledge_tok)

        ks_found = knowledge_article != ""
        self.progress_update_queue.put_nowait({"id": 0, "message": f"Knowledge fetched from article {knowledge_article}"
                                               if ks_found else "Knowledge source not found", "success": ks_found})

        # Retrieve the relevant knowledge sentence from the knowledge source
        selected_question, knowledge_sent, knowledge_start_index, knowledge_end_index = "", "", 0, 0
        if len(cur_turn_knowledge_tok) != 0:
            selected_question, knowledge_sent, knowledge_start_index, knowledge_end_index = self.find_relevant_response(
                message, cur_turn_knowledge, cur_turn_knowledge_tok)

        self.progress_update_queue.put_nowait(
            {"id": 1, "message": "Knowledge span extracted" if ks_found else "Knowledge source not found",
             "success": ks_found}
        )

        # Condition on the knowledge sentence, and generate knowledge-grounded dialog
        best_response, knowledge_grounded_responses = \
            self.generate_knowledge_based_response(message, knowledge_sent)

        # Cleaning the responses
        best_response = clean_answer(best_response)
        for i in range(len(knowledge_grounded_responses)):
            knowledge_grounded_responses[i] = clean_answer(knowledge_grounded_responses[i])

        # Logging and Return
        print(f"[{self.TAG}]: get_response: GENERATED RESPONSE: {knowledge_grounded_responses}")
        response = {
            "knowledge_sent": knowledge_sent,
            "response": best_response,
            "candidates": knowledge_grounded_responses,
            "knowledge_source": cur_turn_knowledge,
            "k_start_index": knowledge_start_index,
            "k_end_index": knowledge_end_index,
            "id": 3,
            "message": "Response generated",
            "success": True
        }
        self.progress_update_queue.put_nowait(response)
        return response

    def exit(self):
        print(f"\n\n[{self.TAG}]: Quitting MUKALMA")
        self.knowledge_db.close()
