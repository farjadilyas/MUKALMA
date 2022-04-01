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
  cache can be extended with a persistance mechanism to use a 'hot cache' for subsequent starts.

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


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def extract_paras_and_heads(soup, doc_title, chunk_size=8):
    """
      Returns the (heading, paragraphs) pairs from the page parsed by soup
      Placed a minimum number of sentence limit on paragraph length to ignore insignificant paragraphs
      which skew the results
    """

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
    def __init__(self, model=None, num_results=3):
        # This is a dictionary which keeps track of the content of the article
        # corresponding to their identifier (title)
        self.article_db = {}

        self.num_results = num_results

        self.sentence_model = SentenceTransformer('../../../models/all-MiniLM-L6-v2', device='cuda') if model is None \
            else model

    def fetch_topic_data(self, topics, message):
        topic_search_str = ' '.join(topics)

        print(f"Fetching data for {topic_search_str}")
        articles = wikipedia.search(topic_search_str, results=self.num_results)
        print(f"Using the following relevant articles: {articles}")

        docs_content = []
        articles_data = []
        for article in articles:
            article_data = self.fetch_article_data(article)

            # Ignore article if its data couldn't be scraped
            if article_data is None:
                continue

            docs_content.append(article_data[0])
            articles_data.append(article_data)

        # Obtain the cosine similarity of the message with the relevant articles for the current topic
        if (len(docs_content) == 0):
            return []
            
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
        print(f"SELECTED PARA ID: {selected_para_id}, {len(para_c_sim)}")
        print(f"======= SELECTED PARAGRAPH:\n{mini_docs[selected_para_id]}")

        return mini_docs[selected_para_id]

    def fetch_article_data(self, title):
        article_db_entry = self.article_db.get(title, None)
        if article_db_entry is not None:
            print(f"Topic '{title}' has already been cached")
            return article_db_entry

        print(f"Topic '{title}' has not been cached, fetching and building...")

        # Fetch and scrape the contents of the wikipedia page corresponding to the title
        page = requests.get(f"https://en.wikipedia.org/wiki/{title}")
        soup = BeautifulSoup(page.content, 'lxml')

        article_data = extract_paras_and_heads(soup, title)

        # If no paragraphs could be retrieved, this article is useless
        if article_data is None:
            return None

        heads, paras = article_data

        # Use the heads, paras pairs (mini-documents) to calculate TF-IDF embeddings...
        # for the set of mini-documents of the article corresponding to title
        # These embeddings can be used to find which mini_doc is most similar to a given document
        # TODO: The heading of the document MAY BE appended before every sentence so that...
        # the absence of the heading in a sentence doesn't make it irrelevant

        # Save tokenized paragraph sentences for QA, and process the paragraph text for calculating embeddings
        content = ""
        mini_docs = []
        processed_paras = []
        for i in range(len(paras)):
            para_tok = nltk.tokenize.sent_tokenize(paras[i])
            if len(para_tok) <= 1:
                continue

            # Accumulate the total content of the article
            content = f"{content} {paras[i]}"

            # Append the heading corresponding to the paragraph before every sentence in the paragraph
            # Replace the paragraph with this processed paragraph
            # This processed paragraph will be used to calculate the TF-IDF embeddings
            para_head = heads[i] if i < len(heads) else ""
            processed_para = ""
            for para_sent in para_tok:
                processed_para = f"{processed_para} {para_head} {para_sent}"
            # paras[i] = processed_para
            processed_paras.append(paras[i])

            # Save the tokenized sentences for this paragraph, NOTE: these use the original sentences
            # If this paragraph gets selected as the most relevant one...
            # Then this list of tokenized sentences will be used for question answering
            mini_docs.append(para_tok)

        paras = processed_paras

        # Calculate mini_doc embeddings using the processed paragraphs
        mini_doc_embeddings = self.sentence_model.encode(paras)

        # For this new article, save the following:
        # entire article text content: used to calculate document-level embeddings when selecting most relevant document
        # embeddings of the mini docs of this article: used when selecting the most-relevant paragraph
        # the tokenized sentences of the mini docs of this article: uses when applying QA to the most relevant paragraph
        article_db_entry = (content, mini_doc_embeddings, mini_docs)
        self.article_db[title] = article_db_entry

        return article_db_entry
