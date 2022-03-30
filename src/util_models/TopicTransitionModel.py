"""
  MUKALMA - A Knowledge-Powered Conversational Agent
  Project Id: F21-20-R-KBCAgent

  Class that is responsible for keeping track of the topic a moving conversation is centered around.
  It detects changes in topics and updates its information about the current topic after every conversation turn.
  If it decides that the topic has changed, it will look for a new central topic.
  If the topic is the same, it will slightly tweak the focus of the conversation.

  @Author: Muhammad Farjad Ilyas
  @Date: 29th March 2022
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from torch.cuda import is_available as is_cuda_available
from scipy.cluster.vq import kmeans


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
    """

    __control_msg = "Hey! How are you doing?"

    def __init__(self, model=None, model_path='../../models/all-MiniLM-L6-v2', use_cuda=False):
        self.keywords = []
        self.cur_topic_desc_keywords = []
        self.prev_msg = TopicTransitionModel.__control_msg

        # Keeps track of whether the topic changed in the previous turn
        self.topic_changed = False

        self.FALSE_TOPIC_CHANGE_LIMIT = 3
        self.false_topic_change = 0

        self.model = SentenceTransformer(
            model_path, device=('cuda' if use_cuda and is_cuda_available() else 'cpu')
        ) if model is None else model

    def calc_sentence_similarity(self, msg, candidates):
        msg_embedding = self.model.encode([msg])
        candidate_embeddings = self.model.encode(candidates)
        distances = cosine_similarity(msg_embedding, candidate_embeddings).flatten()
        return distances

    def has_topic_changed(self, msg, prev_msg, control_msg):
        distances = self.calc_sentence_similarity(msg, [prev_msg, control_msg])
        max_id = distances.argmax()
        return max_id == 1

    def update_topic(self, message, c_keywords):
        topic_change_detected = self.has_topic_changed(message, self.prev_msg, TopicTransitionModel.__control_msg)

        if topic_change_detected and len(c_keywords) == 0 and self.false_topic_change < self.FALSE_TOPIC_CHANGE_LIMIT:
            self.false_topic_change += 1
            topic_change_detected = False

        if topic_change_detected:
            self.keywords = t_keywords = c_keywords
            print(f"topic has changed to {self.keywords}")
            self.topic_changed = True
        else:
            if self.topic_changed:
                self.topic_changed = False

                # Compare the current sentence against the keywords in the previous turn and keep the most relevant ones
                # until the topic changes
                if len(self.keywords) > 3:
                    scores = self.calc_sentence_similarity(message, self.keywords)
                    self.cur_topic_desc_keywords = [self.keywords[i] for i in find_highest_similarity_scores(scores)]
                else:
                    self.cur_topic_desc_keywords = self.keywords
                    self.keywords = []
                t_keywords = list(set(c_keywords) | set(self.cur_topic_desc_keywords) | set(self.keywords))
            else:
                # It's been >2 turns since the topic changed
                t_keywords = list(set(c_keywords) | set(self.cur_topic_desc_keywords) | set(self.keywords))
                if len(t_keywords) > 0:
                    s_scores = self.calc_sentence_similarity(message, t_keywords)
                    print(f"scores: {s_scores}")
                    s_idxs = list_sorted_args(s_scores, reverse=True)
                    print(f"s_idxs: {s_idxs}")
                    t_keywords = [t_keywords[i] for i in s_idxs]

            if self.keywords is None:
                self.keywords = []
            print(f"topic has not changed, keywords: {t_keywords}")
            self.keywords = c_keywords

        self.prev_msg = message
        return t_keywords
