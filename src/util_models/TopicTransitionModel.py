"""
  MUKALMA - A Knowledge-Powered Conversational Agent
  Project Id: F21-20-R-KBCAgent

  Class that is responsible for keeping track of the topic a moving conversation is centered around.
  It detects changes in topics and updates its information about the current topic after every 
  conversation turn.
  If it decides that the topic has changed, it will look for a new central topic.
  If the topic is the same, it will slightly tweak the focus of the conversation.

  @Author: Muhammad Farjad Ilyas, Nabeel Danish
  @Date: 31st March 2022
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from torch.cuda import is_available as is_cuda_available
from scipy.cluster.vq import kmeans

import numpy as np

def list_sorted_args(l, reverse=False):
    return sorted(range(len(l)), key=l.__getitem__, reverse=reverse)


def find_highest_similarity_scores(scores, n=3):
    s_idxs = list_sorted_args(scores)
    s = [scores[i] for i in s_idxs]
    s_len = len(s)
    s_range = range(s_len)

    kclust = kmeans(np.matrix([s_range, s]).transpose(), n)
    assigned_clusters = [abs(kclust[0][:, 0] - e).argmin() for e in s_range]
    print(assigned_clusters)

    highest_cluster = assigned_clusters[-1]
    highest_idxs = []
    for i in range(s_len - 1, -1, -1):
        if assigned_clusters[i] != highest_cluster:
            return highest_idxs
        highest_idxs.append(s_idxs[i])
    return highest_idxs


class TopicTransitionModel:
    """
      Compares the current message with the previous message and a control message using sentence similarity.
      Uses the intuition that if the current message is closer to the generic control message that doesn't involve
      a particular topic, compared to a possibly topic-related previous message, then the topic may have changed.

      Updates the keywords that are relevant to the conversation by detecting topic changes. Gives a higher priority
      to keywords that have occurred recently by placing them earlier in the list of keywords in ascending order of
      indexing.
      
      Uses a filtering method to pass previous keywords that are still relevant to the conversation turn. This 
      helps the model simulate conversation context and aids in topic change
    """

    __control_msg = "Hey! How are you doing?"

    def __init__(self, model=None, model_path='../../models/all-MiniLM-L6-v2', use_cuda=False):
        # Keeping track of previous message and keywords that will pass forward
        self.sent_changed_topic = self.prev_msg = TopicTransitionModel.__control_msg
        self.prev_keywords = []
        self.pass_through = []
        self.c_keywords = []    # Remember current keywords in case a safer version of current turn keywords is required

        # Keeping track of False Postives
        self.FALSE_TOPIC_CHANGE_LIMIT = 3
        self.false_topic_change = 0

        # Sentence transformer model
        self.model = SentenceTransformer(
            model_path, device=('cuda' if use_cuda and is_cuda_available() else 'cpu')
        ) if model is None else model

    def calc_sentence_similarity(self, msg, candidates):
        msg_embedding = self.model.encode([msg])
        candidate_embeddings = self.model.encode(candidates)
        distances = cosine_similarity(msg_embedding, candidate_embeddings).flatten()
        return distances

    def order_keywords_by_similarity(self, msg, keywords):
        if len(keywords) == 0:
            return []

        s_scores = self.calc_sentence_similarity(msg, keywords)
        s_idxs = list_sorted_args(s_scores, reverse=True)
        t_keywords = [keywords[i] for i in s_idxs]
        return t_keywords

    def has_topic_changed(self, msg, prev_msg, control_msg, error_threshold = -0.02):
        distances = self.calc_sentence_similarity(msg, [prev_msg, control_msg])
        return (distances[1] - distances[0]) > error_threshold

    def update_topic(self, message, c_keywords):
        
        # Comparing the current message to the previous keywords
        if len(self.prev_keywords) > 0:
            self.prev_keywords = list(set(self.prev_keywords).difference(c_keywords)) 
            s_scores = self.calc_sentence_similarity(message, self.prev_keywords)

            if len(self.prev_keywords) >= 3:
                self.pass_through = [self.prev_keywords[i] for i in find_highest_similarity_scores(s_scores, 2 if len(self.prev_keywords) <= 3 else 3)]
            else:
                self.pass_through = self.prev_keywords
        # End if
        
        # Calculating topic changes
        topic_change_from_prev_msg = self.has_topic_changed(message, self.prev_msg, TopicTransitionModel.__control_msg)
        topic_change_from_prev_topic = self.has_topic_changed(message, self.sent_changed_topic, TopicTransitionModel.__control_msg, error_threshold=0.05)

        # If topic changes
        if topic_change_from_prev_msg or topic_change_from_prev_topic:    
            self.sent_changed_topic = message
            
        # Adding new keywords
        t_keywords = c_keywords + self.pass_through

        if len(t_keywords) > 0:
            t_keywords = self.order_keywords_by_similarity(message, t_keywords)
        
        # Setting Previous keywords
        self.prev_msg = message
        self.prev_keywords = t_keywords

        self.c_keywords = c_keywords
        return t_keywords
    # End of function

    def report_topic_change(self):
        """
          Tells this TopicTransitionModel that the current turn it just processed did, in fact, introduce a change in
          the topic. This method serves as a form of feedback to this model, so it can adjust its parameters and
          consider this turn to be the start of a new topic
        :return: The keywords extracted from this turn alone, with pass-through keywords no longer being considered
        """

        # Set prev_keywords, to be used for the next turn, to t_keywords, minus pass-through keywords, which is
        # equivalent to c_keywords
        self.prev_keywords = self.c_keywords
        self.pass_through = []
        return self.c_keywords
    
# End of class
