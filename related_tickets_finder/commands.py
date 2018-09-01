import click
import logger
from pprint import pformat
import json
import configparser
import os

from common_util import project_dir_path
import jira_scraper.jira_worker as scraper
import related_tickets_finder.similar_ticket_finder as related_tickets_finder_module
import related_tickets_finder.util as related_tickets_pkg_util

#constant
THIS_MODULE_DIRECTORY = os.path.join(project_dir_path, 'related_tickets_finder')
CONFIG_DIRECTORY = os.path.join(THIS_MODULE_DIRECTORY, 'settings')

# reading jql filters
jql_filters = configparser.ConfigParser()
jql_filters_config_file = os.path.join(CONFIG_DIRECTORY,'jql_filters_to_scrape.config')
jql_filters.read(jql_filters_config_file)
model_config = configparser.ConfigParser()
model_config_file = os.path.join(CONFIG_DIRECTORY,'current_model_in_use.config')
model_config.read(model_config_file)

@click.command()
def train_related_tickets_model():
    """This runs a script to train model on all closed tickets"""
    try:
        jira_obj = scraper.connect_to_jira()

        # read jql filters config
        filter_to_get_completed_tickets_for_training = dict(jql_filters['FILTER_COMPLETED_TICKETS_FOR_TRAINING'])

        # for each filter, train and save a model
        for filter_name, filter_query in filter_to_get_completed_tickets_for_training.items():
            logger.logger.info("Will crawl " + filter_name)
            jira_tickets_corpus = scraper.filter_crawler(jira_obj, filter_query)
            logger.logger.info("Crawling of " + filter_name + " done.")
            related_tickets_finder_module.train_and_save_tfidf_model(jira_tickets_corpus, "model_" + filter_name)

    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()



@click.command()
@click.option('--test-model', help='Find related tickets for given model.')
@click.option('--open-tickets-filter',
              help='Use this filter to find related tickets to tickets given by this filter. Please provide test-model also if you pass a value for this arg. If this argument is not given, it picks up default filters.')
def comment_related_tickets(test_model, open_tickets_filter):
    """This runs a script to comment related tickets on each new ticket for configured filters"""
    try:
        jira_obj = scraper.connect_to_jira()

        # read jql filters config
        filters_to_get_new_tickets = dict(jql_filters['FILTER_OPEN_NEW_TICKETS'])

        # finalize filter to be used right now
        default_filters = filters_to_get_new_tickets
        if open_tickets_filter is not None:
            filter_to_use = {'custom': open_tickets_filter}
        else:
            filter_to_use = default_filters
        logger.logger.info("Filter I'm using : " + pformat(filter_to_use))

        # for each filter, find its tickets and comment related tickets using the model
        for filter_name, filter_query in filter_to_use.items():
            # crawl and get tickets info for this filter
            jira_tickets_corpus = scraper.filter_crawler(jira_obj, filter_query)

            # get info about tickets in which related tickets have already been commented
            already_commented_tickets_file = os.path.join(os.path.join(THIS_MODULE_DIRECTORY,'data'),
                                                          filter_name+'_already_commented_tickets.json')
            related_tickets_pkg_util.create_already_commented_tickets_file_if_not_exists(
                already_commented_tickets_file)
            with open(already_commented_tickets_file, 'r') as data_file:
                tickets_already_commented = json.load(data_file)

            # find the set of tickets which are new and require a comment
            new_tickets_corpus = [ticket for ticket in jira_tickets_corpus if
                                  ticket['jiraid'] not in tickets_already_commented]
            if not new_tickets_corpus:
                logger.logger.info("No new tickets to comment on from " + filter_name + ". Moving on to next filter.")
                continue

            # find the model pickle file to be used
            model_file_path = related_tickets_pkg_util.get_model_file_path(filter_name, test_model)

            # find top N related tickets
            related_tickets_data = related_tickets_finder_module.find_top_n_related_jira_tickets(5, new_tickets_corpus,
                                                                                                 model_file_path)

            # for each ticket, comment the top N related tickets to it
            for ticket in related_tickets_data:
                logger.logger.info("Ticket:" + ticket['jiraid'] + "| Related tickets:" + str(ticket['related_tickets']))
                scraper.comment_on_task(jira_obj, ticket['jiraid'], related_tickets_pkg_util.get_formatted_comment(
                    ticket['related_tickets']))
                tickets_already_commented.append(ticket['jiraid'])

            # update the already commented list file
            logger.logger.info(tickets_already_commented)
            with open(already_commented_tickets_file, 'w') as outfile:
                json.dump(tickets_already_commented, outfile)
            logger.logger.info("Done for " + str(filter_name))
        logger.logger.info("Execution completed.")
    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()



@click.command()
@click.option('--type-of-data', type=click.Choice(['default-filters-for-training', 'default-filters-for-commenting',
                                           'current-models', 'tickets-alread-commented']), help='Choose one of these '
                                                                                                'options to retrieve data')
def get_data(type_of_data):
    """ This command returns data that is being used in the script when it gets run by cron."""
    if (type_of_data == 'default-filters-for-training'):
        logger.logger.info(dict(jql_filters['FILTER_COMPLETED_TICKETS_FOR_TRAINING']))
    elif (type_of_data == 'default-filters-for-commenting'):
        logger.logger.info(dict(jql_filters['FILTER_OPEN_NEW_TICKETS']))
    elif (type_of_data == 'current-models'):
        logger.logger.info(dict(model_config['FILTER_MODEL_MAP']))
    elif (type_of_data == 'tickets-alread-commented'):
        for filter_name in dict(jql_filters['FILTER_OPEN_NEW_TICKETS']).keys():
            already_commented_tickets_file = os.path.join(os.path.join(THIS_MODULE_DIRECTORY, 'data'),
                                                          filter_name+'_already_commented_tickets.json')
            with open(already_commented_tickets_file, 'r') as json_file:
                tickets_already_commented = json.load(json_file)
            logger.logger.info("Tickets already commented for " + filter_name + ": " + str(tickets_already_commented))
    else:
        logger.logger.error("Couldn't understand.")
    pass
