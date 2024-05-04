import spacy
from spacy.lang.en.stop_words import STOP_WORDS as STOPWORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
word_vectorizer = TfidfVectorizer(
    sublinear_tf=True,    
    max_features=1500)
import numpy as np
import re

nlp = spacy.load("en_core_web_sm")

def clean_text(text: str, remove_stopwords: bool=False, lemmatize: bool = False):
    text = text.replace("\n", " ").lower()
    text = re.sub('http\S+\s*', ' ', text)  # remove URLs
    text = re.sub('RT|cc', ' ', text)  # remove RT and cc
    text = re.sub('#\S+', '', text)  # remove hashtags
    text = re.sub('@\S+', '  ', text)  # remove mentions
    text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', text)  # remove punctuations     
    text = re.sub('\s+', ' ', text)  # remove extra whitespace
    text = re.sub('\W', ' ', text)
    doc = nlp(text)
    tokens = [token.text for token in doc]
    skills = [ent.text for ent in doc.ents if ent.label_=="SKILL"]
    if lemmatize:        
        tokens = [token.lemma_ for token in doc]
    if remove_stopwords:
        tokens = [token for token in tokens if token not in STOPWORDS]
    return ' '.join(tokens)


def get_similarity(resume_text, jd_text):
    word_vectorizer.fit([resume_text, jd_text])
    tfidf_resume_vectors = word_vectorizer.transform([resume_text])
    tfidf_jd_vectors = word_vectorizer.transform([jd_text])
    tfidf_similarity = np.mean(cosine_similarity(tfidf_resume_vectors, tfidf_jd_vectors))
    return round(tfidf_similarity*100, 2)

def score_resume(resume_text: str, jd_text: str):
    resume_text = clean_text(resume_text)    
    jd_similarity = get_similarity(resume_text, jd_text)        
    return jd_similarity



