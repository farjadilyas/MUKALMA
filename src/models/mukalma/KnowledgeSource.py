"""
  MUKALMA - A Knowledge-Powered Conversational Agent
  Project Id: F21-20-R-KBCAgent

  Knowledge Source class for the MUKALMA model.
  MUKALMA uses the selected knowledge source in a variety of forms.
  It may also exxtend and augment the knowledge source according to the flow of the conversation.
  This class encapsulates all forms of the knowledge source and provides methods for controlling it.

  Although it is possible to fetch all the knowledge MUKALMA requires anew for every turn,
  it is desirable to keep a cache of the topics searched for, the articles that are relevant to them,
  their content, and their pre-computed embeddings since it is likely the conversation will revolve
  around a given topic for multiple turns.

  Additionally, in the absence of the network connectivity required to build this cache, this
  cache can be extended with a persistence mechanism to use a 'hot cache' for subsequent starts.

  @Author: Muhammad Farjad Ilyas
  @Date: 22nd March 2022
"""

# Import for scraping data off the web
import requests
import wikipedia
from bs4 import BeautifulSoup
import re
import nltk

# Import SentenceTransformer for using a Sentence Embedding model
from sentence_transformers import SentenceTransformer

# Imports for Document Similarity computation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# For dividing lists into smaller chunks
from itertools import islice

# For saving the KnowledgeSource object, so next time the cache can be loaded in a hot state
import pickle
from os.path import exists

SINGLE_KS_FILENAME = 'knowledge_source.pkl'
MULTI_KS_FILENAME = 'multi_knowledge_source.pkl'


def merge_db(db1_filename, db2_filename, target_filename):
    target_db = None
    db1 = read_object(db1_filename)
    db2 = read_object(db2_filename)

    if db1 is None and db2 is not None:
        target_db = db2
    elif db1 is not None and db2 is None:
        target_db = db1
    elif db1 is not None and db2 is not None:
        target_db = db1.copy()
        target_db.update(db2)

    if target_db is not None:
        save_object(target_db, target_filename)
        return True
    return False


def save_object(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def read_object(filename):
    obj = None
    try:
        if exists(filename):
            print(f"{filename} exists")
            with open(filename, 'rb') as inp:
                obj = pickle.load(inp)
    except (FileNotFoundError, PermissionError):
        pass
    return obj


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def extract_paras_and_heads(doc_title, chunk_size=8):
    """
      Returns the (heading, paragraphs) pairs from the page parsed by soup
      Placed a minimum number of sentence limit on paragraph length to ignore insignificant paragraphs
      which skew the results
    """

    # Fetch and scrape the contents of the wikipedia page corresponding to the title
    page = requests.get(f"https://en.wikipedia.org/wiki/{doc_title}")
    soup = BeautifulSoup(page.content, 'lxml')

    # Extract paragraph text, ignoring any empty class paragraphs
    # Fetch the intro paragraph separately since it isn't associated with a heading
    # Handles the case of multiple paragraphs under a single ehading
    paras = []
    all_paragraphs = soup.find_all('p', class_=lambda x: x != 'mw-empty-elt')
    intro_para = ""

    for p_id, paragraph in enumerate(all_paragraphs):
        p_text = re.sub(r"\[.*?\]+", '', paragraph.text)
        p_tok = nltk.tokenize.sent_tokenize(p_text)
        if p_id == 0:
            intro_para = p_text
        elif len(p_tok) > 1:
            paras.extend([' '.join(p_chunk) for p_chunk in chunk(p_tok, chunk_size)])

    # Extract text from paragraph headers
    heads = []
    for head in soup.find_all('span', attrs={'mw-headline'}):
        heads.append(str(head.text))

    if len(paras) == 0:
        return None

    # The first paragraph is the introductory paragraph and doesn't have a heading
    # Set its heading as the document title
    heads.insert(0, doc_title)
    paras.insert(0, intro_para)

    """
    for i in range(len(paras)):
        if len(nltk.tokenize.sent_tokenize(paras[i])) > 1:
            print(paras[i], "\n")
    """
    return heads, paras


def calculate_tfidf_similarity(base_document, documents):
    # To make uniformed vectors, both documents need to be combined first.
    d = [base_document]
    d.extend(documents)

    # TODO: Hyper-parameter tuning of TF-IDF vectorizer for calculating document embeddings
    vectorizer = TfidfVectorizer(stop_words='english', binary=True, ngram_range=(1, 3), analyzer='char', lowercase=True)
    embeddings = vectorizer.fit_transform(d)
    print(embeddings.shape, len(d))

    cosine_similarities = cosine_similarity(embeddings[0:1], embeddings[1:]).flatten()
    print(f"DOCUMENT COSINE SIM: {cosine_similarities}")
    return cosine_similarities


class KnowledgeSource:
    def __init__(self, model=None, num_results=3, persist=True, persist_path='', use_hot_cache=True):
        self.use_multi_source = num_results > 1
        if self.use_multi_source:
            self.ks_filename = MULTI_KS_FILENAME
        else:
            self.ks_filename = SINGLE_KS_FILENAME

        # Initialize knowledge source, optionally from a previously persisted file
        # For each cached article, this dictionary stores the article's overall content, its mini paragraphs, and the
        # precomputed embeddings corresponding to the mini paragraphs
        persist_location = persist_path + \
                           ('/' if persist_path != '' and persist_path[-1] != '/' else '') + self.ks_filename
        ks = read_object(persist_location) if use_hot_cache else None
        if ks is None:
            print("CREATING NEW KNOWLEDGE SOURCE")
            self.article_db = {}
        else:
            print("USING PERSISTED KNOWLEDGE SOURCE")
            self.article_db = ks

        self.num_results = num_results

        self.sentence_model = SentenceTransformer('../../../models/all-MiniLM-L6-v2', device='cuda') if model is None \
            else model

        # Whether the knowledge source object should be persisted at the end of execution
        self.persist = persist
        self.persist_location = persist_location if persist else None

    def build_db(self, topics):
        """
          Given a list of topics, each consisting of a list of keywords corresponding to the topic, build a database of
          articles consisting of an num_articles articles for each topic in the list. Stores the overall content,
          breaks down the content of the article into mini docs, and precomputes embeddings corresponding to these mini
          docs.
        """
        for topic_keywords in topics:
            topic_search_str = ' '.join(topic_keywords)

            print(f"Fetching data for {topic_search_str}")
            articles = wikipedia.search(topic_search_str, results=self.num_results)
            print(f"Using the following relevant articles: {articles}")

            # For every article corresponding to the topic, fetch and save its overall content and embeddings
            # corresponding to the mini paragraphs of the article
            for article in articles:
                if self.use_multi_source:
                    self.__fetch_multi_source_article_data(article)
                else:
                    self.__fetch_single_source_article_data(article)

    def fetch_relevant_articles(self, topics):
        if len(topics) == 0:
            return []

        topic_search_str = ' '.join(topics)

        print(f"Fetching data for '{topic_search_str}'")
        try:
            articles = wikipedia.search(topic_search_str, results=self.num_results)
        except:
            articles = []
        print(f"Using the following relevant articles: {articles}")

        return articles

    def fetch_topic_data(self, topics, message):
        selected_para_tok, selected_article_title = self.__fetch_multi_source_topic_data(topics, message) \
            if self.use_multi_source else self.__fetch_single_source_topic_data(topics, message)
        print(f"======= SELECTED PARAGRAPH:\n{selected_para_tok}")
        return selected_para_tok, selected_article_title

    def __fetch_multi_source_topic_data(self, topics, message):
        articles = self.fetch_relevant_articles(topics)

        if len(articles) == 0:
            return [], ""

        topic_paras = []    # Mini paragraphs comprising all mini paragraphs of each article relevant to the topic
        for article in articles:
            article_paras = self.__fetch_multi_source_article_data(article)

            if article_paras is not None:
                topic_paras.extend(article_paras)

        if len(topic_paras) == 0:
            return [], ""

        # Once the topic paras have been accumulated, the embeddings for them, and the most similar para can be found
        topic_paras_embeddings = self.sentence_model.encode(topic_paras)

        # Encode the input message, and use the topic para embeddings to calculate cosine similarity
        # The resulting scores can be used to find the most similar paragraph in all articles relevant to the topic
        para_c_sim = cosine_similarity(self.sentence_model.encode([message]), topic_paras_embeddings).flatten()
        selected_para_id = para_c_sim.argmax()

        return nltk.tokenize.sent_tokenize(topic_paras[selected_para_id]), articles[0]

    def __fetch_multi_source_article_data(self, title):
        article_paras = self.article_db.get(title, None)
        if article_paras is not None:
            print(f"Topic '{title}' has already been cached")
        else:
            print(f"Topic '{title}' has not been cached, fetching and building...")
            article_data = extract_paras_and_heads(title, chunk_size=3)

            if article_data is not None:
                heads, article_paras = article_data
                # Obtained mini docs from the article data, and filter out paragraphs that are too short
                processed_paras = []
                for i in range(len(article_paras)):
                    para_tok = nltk.tokenize.sent_tokenize(article_paras[i])
                    if len(para_tok) <= 1:
                        continue
                    processed_paras.append(article_paras[i])
                article_paras = processed_paras

                # Cache article paras
                self.article_db[title] = article_paras
            else:
                print(f"Data for '{title}' could not be parsed, ignoring this article")

        return article_paras

    def __fetch_single_source_topic_data(self, topics, message):
        articles = self.fetch_relevant_articles(topics)

        if articles is None or len(articles) == 0:
            return [], ""

        docs_content = []
        articles_data = []
        for article in articles:
            article_data = self.__fetch_single_source_article_data(article)

            # Ignore article if its data couldn't be scraped
            if article_data is None:
                continue

            docs_content.append(article_data[0])
            articles_data.append(article_data)

        # Obtain the cosine similarity of the message with the relevant articles for the current topic
        if len(docs_content) == 0:
            return [], ""

        doc_c_sim = calculate_tfidf_similarity(message, docs_content)

        # Select the most similar article
        selected_article_id = doc_c_sim.argmax()
        print(f"'{articles[selected_article_id]}' has been selected as the most relevant article")

        # Now, select the most relevant mini doc (chunk of one or more paragraphs) in the most relevant article
        selected_article_data = articles_data[selected_article_id]
        mini_doc_embeddings, mini_docs = selected_article_data[1], selected_article_data[2]

        # Calculate embedding for the input message using the saved vectorizer for this article
        # Use this with the pre-calculated embeddings for the paragraphs in the article to calculate cosine similarity
        para_c_sim = cosine_similarity(self.sentence_model.encode([message]), mini_doc_embeddings).flatten()
        selected_para_id = para_c_sim.argmax()

        return mini_docs[selected_para_id], articles[selected_article_id]

    def __fetch_single_source_article_data(self, title):
        article_db_entry = self.article_db.get(title, None)
        if article_db_entry is not None:
            print(f"Topic '{title}' has already been cached")
            return article_db_entry

        print(f"Topic '{title}' has not been cached, fetching and building...")

        article_data = extract_paras_and_heads(title, chunk_size=3)

        # If no paragraphs could be retrieved, this article is useless
        if article_data is None:
            return None

        heads, paras = article_data

        # Use the heads, paras pairs (mini-documents) to calculate TF-IDF embeddings...
        # for the set of mini-documents of the article corresponding to title
        # These embeddings can be used to find which mini_doc is most similar to a given document
        # the absence of the heading in a sentence doesn't make it irrelevant

        # Save tokenized paragraph sentences for QA, and process the paragraph text for calculating embeddings
        content = ""
        mini_docs = []
        for i in range(len(paras)):
            para_tok = nltk.tokenize.sent_tokenize(paras[i])
            if len(para_tok) <= 1:
                continue

            # Accumulate the total content of the article
            content = f"{content} {paras[i]}"

            # Save the tokenized sentences for this paragraph, NOTE: these use the original sentences
            # If this paragraph gets selected as the most relevant one...
            # Then this list of tokenized sentences will be used for question answering
            mini_docs.append(para_tok)

        # Calculate mini_doc embeddings using the processed paragraphs
        mini_doc_embeddings = self.sentence_model.encode(paras)

        # For this new article, save the following:
        # entire article text content: used to calculate document-level embeddings when selecting most relevant document
        # embeddings of the mini docs of this article: used when selecting the most-relevant paragraph
        # the tokenized sentences of the mini docs of this article: uses when applying QA to the most relevant paragraph
        article_db_entry = (content, mini_doc_embeddings, mini_docs)
        self.article_db[title] = article_db_entry

        return article_db_entry

    def close(self):
        """
         Save the knowledge acquired over the course of Knowledge Source's lifetime to disk
        """
        if not self.persist:
            return
        save_object(self.article_db, self.persist_location)


if __name__ == '__main__':
    uin = input(f"{'=' * 100}\nKnowledgeSource save file merger\n{'=' * 100}\n\nContinue (y/n)?")
    if uin.strip().lower() == 'n':
        print("Quitting...")
        exit()

    db1_fn = input('Enter db1 file path and name (can be relative): ')
    db2_fn = input('Enter db2 file path: ')
    target_db_fn = input('Enter target db file path: ')
    merge_result = merge_db(db1_fn, db2_fn, target_db_fn)
    print("Merge", "successful" if merge_result else "failed. Check the source files and try again.")
