import re
from jira import JIRA
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

import jira_scraper.settings.jira_auth as auth
import logger

maxResultsToReturn = 2000
stops = set(stopwords.words("english"))
stemmer = SnowballStemmer('english')


def connect_to_jira():
    logger.logger.info("Connecting to JIRA.")
    return JIRA(auth.jira_url, auth=(auth.jira_username,auth.jira_password))

def remove_code_from_comments(comment_body):
    return re.sub(r'{code:.*}([\s\S]*?){code}','',str(comment_body))

def get_jira_issue_object(authed_jira, jira_name):
    return authed_jira.issue(jira_name)

def get_title(jira_issue_object):
    return jira_issue_object.fields.summary

def get_summary(jira_issue_object):
    return jira_issue_object.fields.description

def get_jira_id(jira_issue_object):
    return jira_issue_object.key

def get_status(jira_issue_object):
    return jira_issue_object.fields.status

def get_list_of_comments(jira_issue_object):
    return jira_issue_object.fields.comment.comments

def get_reqd_comments_data(list_of_comments_object):
    ticket_dict = {'comments_data':[], 'comments_corpus':[]}
    for comment in list_of_comments_object:
        comment_data = {}
        if comment.author.emailAddress:
            comment_data['emailAddress'] = comment.author.emailAddress
        comment_data['body'] = comment.body
        comment_data['created'] = comment.created
        comment_data['updated'] = comment.updated
        comment_data['displayName'] = comment.author.displayName
        comment_data['name'] = comment.author.name
        ticket_dict['comments_data'].append(comment_data)
        comment_corpus_data = remove_code_from_comments(comment_data['body'])
        ticket_dict['comments_corpus'].append(comment_corpus_data)
    return ticket_dict['comments_data'],ticket_dict['comments_corpus']

def get_assignee_name(jira_issue_object):
    if jira_issue_object.fields.assignee:
        return jira_issue_object.fields.assignee.displayName
    ticket_id = get_jira_id(jira_issue_object)
    logger.logger.error(str(ticket_id)+":No name of assignee found. Please fix.")
    return ""

def get_assignee_email(jira_issue_object):
    if jira_issue_object.fields.assignee:
        return jira_issue_object.fields.assignee.emailAddress
    ticket_id = get_jira_id(jira_issue_object)
    logger.logger.error(str(ticket_id)+":No email of assignee found. Please fix.")
    return ""

# todo (high) - make inclusion of comments easily configurable
def filter_crawler(authed_jira, jira_filter, include_comments=False):
    logger.logger.debug("Crawling the filter - " + jira_filter)
    filter_tickets = authed_jira.search_issues(jira_filter, maxResults=maxResultsToReturn)
    tickets_corpus = []
    if filter_tickets:
        logger.logger.info("Total tickets to crawl : "+str(len(filter_tickets)))
        one_tenth = len(filter_tickets)/10
        percentage_crawled = 0
        for i,ticket in enumerate(filter_tickets):
            ticket_dict = {}
            jira_id = get_jira_id(ticket)
            ticket_dict['jiraid'] = jira_id
            ticket_dict['title'] = get_title(ticket)
            ticket_dict['summary'] = get_summary(ticket)
            ticket_dict['assigneeName'] = get_assignee_name(ticket)
            ticket_dict['assigneeEmail'] = get_assignee_email(ticket)
            ticket_dict['linked_issues_data'] = ticket.fields.issuelinks
            if(include_comments==True):
                ticket_full_data = authed_jira.issue(jira_id)
                list_of_comments = get_list_of_comments(ticket_full_data)
                ticket_dict['comments_data'],ticket_dict['comments_corpus'] = get_reqd_comments_data(list_of_comments)
            tickets_corpus.append(ticket_dict)
            if i % one_tenth == 0:
                percentage_crawled += 10
                logger.logger.info(str(percentage_crawled)+"% tickets done.")
    logger.logger.debug("Crawling done. Ticket corpus - " + str(tickets_corpus))
    return tickets_corpus

def comment_on_task(authed_jira,jira_id,comment):
    logger.logger.debug("Commenting - " + str(comment) + " on ", jira_id)
    try:
        authed_jira.add_comment(jira_id,comment)
    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()
