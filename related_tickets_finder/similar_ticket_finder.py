import datetime
import pickle

import re
import logger
# import related_tickets_finder.settings.words_to_ignore as ignored_collection
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from common_util import project_dir_path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

stops = set(stopwords.words("english"))
stemmer = SnowballStemmer('english')

def clean_document(document_of_words):
    document_of_words = document_of_words.lower()
    # remove a number or decimal num followed by a space
    document_of_words = re.sub('\\b\d+(?:\.\d+)?\s*', '', document_of_words)
    # remove rid, id fields
    document_of_words = re.sub('[rc]*id\s*:*', '', document_of_words)
    # remove all non-words (make a list)
    document_of_words = re.split('\W+', document_of_words)
    # remove stop words
    document_of_words = [w for w in document_of_words if not w in stops]
    # remove ignored words
    ignored_words = "issue, client, ticket, https, screenshot, support, following, name, getting, kindly, please, reference, backend, yesterday, answer, searched"
    document_of_words = [w for w in document_of_words if not w in ignored_words.split()]
    # stem each word
    stemmed_words = [stemmer.stem(word) for word in document_of_words]
    return ' '.join(stemmed_words)


# NOTE : Currently only picks title and summary as relevant data from a ticket.
def extract_clean_documents_from_corpus(jira_tickets_corpus):
    print("Extracting and Cleaning documents...")
    final_corpus = []
    list_of_docs = []
    i = 0
    for ticket_dict in jira_tickets_corpus:
        document_of_words = (str(ticket_dict['title'])+" "+str(ticket_dict['summary']))
        doc_cleaned_text = clean_document(document_of_words)
        list_of_docs.append(doc_cleaned_text)
        final_corpus.append({'jiraid':ticket_dict['jiraid'], 'words':doc_cleaned_text, 'index':i})
        i+=1
    return list_of_docs,final_corpus



def train_and_save_tfidf_model(jira_tickets_corpus, output_file_name_without_extn):
    tfidf_model = TfidfVectorizer()
    list_of_docs,training_ticket_corpus = extract_clean_documents_from_corpus(jira_tickets_corpus)
    tfidf_trainingset = tfidf_model.fit_transform(list_of_docs)
    trained_model_and_data_dict = {'model':tfidf_model, 'trained_data':tfidf_trainingset, 'corpus':training_ticket_corpus}
    now = datetime.datetime.now()
    model_name_with_path = project_dir_path + "/related_tickets_finder/models/"+output_file_name_without_extn+"_"+str(now.day)+"_"+str(now.month)+"_"+str(now.year)+"_"+str(now.hour)+"_"+str(now.minute)+"_"+str(now.second)+".pickle"
    logger.logger.info("Trained new model name - " + model_name_with_path)
    pickle.dump(trained_model_and_data_dict, open(model_name_with_path, "wb"))
    return model_name_with_path


def load_model(model_file_path):
    with open(model_file_path, 'rb') as pickled_file:
        loaded_model_data = pickle.load(pickled_file)
    return loaded_model_data['model'],loaded_model_data['trained_data'],loaded_model_data['corpus']


def find_top_n_related_jira_tickets(num_of_related_tickets_to_return, input_jira_tickets_corpus, model_file_path):
    logger.logger.info("Will find top " + str(num_of_related_tickets_to_return) + " related tickets")
    model, trained_data_vector, trained_data_corpus = load_model(model_file_path)
    logger.logger.info("Loaded the model and the data from " + model_file_path)
    related_tickets_data = []
    for ticket in input_jira_tickets_corpus:
        ticket_data = ticket['title']
        if ticket['summary'] is not None:
            ticket_data += ticket['summary']
        ticket_data = clean_document(ticket_data)
        test_data_vector = model.transform([ticket_data])

        cosine_similarities = linear_kernel(test_data_vector, trained_data_vector).flatten()
        related_ticket_indices = cosine_similarities.argsort()[:-num_of_related_tickets_to_return-1:-1]

        related_tickets_dict = {}
        related_tickets_dict['jiraid'] = ticket['jiraid']
        related_tickets_dict['related_tickets'] = [trained_data_corpus[i]['jiraid'] for i in related_ticket_indices]
        related_tickets_data.append(related_tickets_dict)
    logger.logger.info("Related tickets data - " + str(related_tickets_data))
    return related_tickets_data