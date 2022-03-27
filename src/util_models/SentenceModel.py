"""
  MUKALMA - A Knowledge-Powered Conversational Agent
  Project Id: F21-20-R-KBCAgent

  SentenceModel model controller class
  - This model provides sentence similarity to a high accuracy level.
  - Computes sentence embeddings, especially useful since similarity scores aren't drastically affected by
  a disparity in the length of input sentences.

  @Author: Muhammad Farjad Ilyas
  @Date: 10th December, 2021
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rich.console import Console
import numpy as np
from torch import cuda

console = Console(record=True)


def softmax(x):
    """
    Function to compute softmax over np-array given x
    :param x: input array to compute softmax over
    :return: return an output array representing x with softmax applies on it to form a probability distribution
    """
    t_x = np.exp(x - np.max(x))
    return t_x / t_x.sum(axis=0)


class SentenceModel:
    def __init__(self, model_path='../../../models/all-mpnet-base-v2', use_cuda=False):
        self.TAG = 'SentenceModel'
        self.model = None

        self.device = 'cuda' if use_cuda and cuda.is_available() else 'cpu'
        cuda.empty_cache()

        self.initialize_model(model_path)

    def initialize_model(self, model_path):
        if self.model is None:
            console.log(f"""[{self.TAG}]: Loading {model_path}...\n""")
            self.model = SentenceTransformer(model_path, device=self.device)

    def get_most_similar_sentence(self, sentence, candidates, num_responses=5):
        sentences = [sentence]
        sentences.extend(candidates)

        sentence_embeddings = self.model.encode(sentences)

        scores = cosine_similarity(
            [sentence_embeddings[0]],
            sentence_embeddings[1:]
        )[0]

        # Compute softmax over the similarity scores for all candidates and pick the best option
        # Softmax is used to obtain a relative score for the best candidate that will work better with a threshold
        scores_softmax = softmax(scores)

        # Traverse over -1*list sorted in ascending order since we want the most similar elements at the smallest indexes
        most_similar_sentences = [candidates[index] for index in (-scores_softmax).argsort()[:num_responses]]
        best_candidate_id = scores_softmax.argmax()
        max_score = scores_softmax[best_candidate_id]
        most_similar_sentence = candidates[best_candidate_id]

        print(f"[{self.TAG}]: get_most_similar_sentence: max score: {max_score}, num_candidates: {len(candidates)},\n" +
              f"score_dist: {scores_softmax}")

        print(f"[{self.TAG}]: returning: {most_similar_sentence}, and {num_responses-1} other similar sentences")
        return most_similar_sentences

    # End of function
# End of class
