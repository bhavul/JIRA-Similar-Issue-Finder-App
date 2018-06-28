import click
import jira_scraper.jira_worker as scraper
import related_tickets_finder.settings.jira_filters_to_scrape as jira_filters
import logger
import related_tickets_finder.related_tickets_finder as related_tickets_finder
from pprint import pformat
from util import project_dir_path
import related_tickets_finder.util as related_tickets_pkg_util
import json
import related_tickets_finder.settings.current_model_for_related_tickets as current_model

@click.command()
def train_related_tickets_model():
    """This runs a script to train model on all closed tickets"""
    try:
        jira_obj = scraper.connect_to_jira()
        for filter_name,filter in jira_filters.filters_to_get_completed_tickets.items():
            logger.logger.info("Will crawl " + filter_name)
            jira_tickets_corpus = scraper.filter_crawler(jira_obj,filter)
            logger.logger.info("Crawling of " + filter_name + " done.")
            related_tickets_finder.train_and_save_tfidf_model(jira_tickets_corpus, "model_" + filter_name)
    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()


@click.command()
@click.option('--test-model', help='Find related tickets for given model.')
@click.option('--open-tickets-filter', help='Use this filter to find related tickets to tickets given by this filter. Please provide test-model also if you pass a value for this arg. If this argument is not given, it picks up default filters.')
def comment_related_tickets(test_model,open_tickets_filter):
    """This runs a script to comment related tickets on each new ticket for configured filters"""
    try:
        jira_obj = scraper.connect_to_jira()
        default_filters = jira_filters.filters_to_get_new_tickets
        if open_tickets_filter is not None:
            filter_to_use = {'custom':open_tickets_filter}
        else:
            filter_to_use = default_filters
        logger.logger.info("Filter I'm using : " + pformat(filter_to_use))
        for filter_name,filter in filter_to_use.items():
            jira_tickets_corpus = scraper.filter_crawler(jira_obj,filter)
            already_commented_tickets_file = project_dir_path + \
                                             "/related_tickets_finder/data/"+filter_name+"_already_commented_tickets" \
                                                                                        ".json"
            related_tickets_pkg_util.create_already_commented_tickets_file_if_not_exists(
                already_commented_tickets_file)
            with open(already_commented_tickets_file, 'r') as data_file:
                tickets_already_commented = json.load(data_file)
            new_tickets_corpus = [ticket for ticket in jira_tickets_corpus if ticket['jiraid'] not in tickets_already_commented]
            if not new_tickets_corpus:
                logger.logger.info("No new tickets to comment on from " + filter_name + ". Moving on to next filter.")
                continue
            model_file_path = related_tickets_pkg_util.get_model_file_path(filter_name, test_model)
            related_tickets_data = related_tickets_finder.find_top_n_related_jira_tickets(5, new_tickets_corpus, model_file_path)
            for ticket in related_tickets_data:
                logger.logger.info("Ticket:" + ticket['jiraid'] + "| Related tickets:" + str(ticket['related_tickets']))
                scraper.comment_on_task(jira_obj, ticket['jiraid'], related_tickets_pkg_util.get_formatted_comment(
                    ticket['related_tickets']))
                tickets_already_commented.append(ticket['jiraid'])
                # break;
            logger.logger.info(tickets_already_commented)
            with open(already_commented_tickets_file,'w') as outfile:
                json.dump(tickets_already_commented, outfile)
            logger.logger.info("Done for " + str(filter_name))
        logger.logger.info("Execution completed.")
    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()


@click.command()
@click.option('--type', type=click.Choice(['default-filters-for-training', 'default-filters-for-commenting',
                                           'current-models', 'tickets-alread-commented']), help='Choose one of these '
                                                                                                'options to retrieve data')
def get_data(type):
    """ This command returns data that is being used in the script when it gets run by cron."""
    if(type=='default-filters-for-training'):
        logger.logger.info(jira_filters.filters_to_get_completed_tickets)
    elif(type=='default-filters-for-commenting'):
        logger.logger.info(jira_filters.filters_to_get_new_tickets)
    elif(type=='current-models'):
        logger.logger.info(current_model.models)
    elif(type=='tickets-alread-commented'):
        for filter_name in jira_filters.filters_to_get_new_tickets.keys():
            already_commented_tickets_file = project_dir_path + \
                                             "/related_tickets_finder/data/"+filter_name+"_already_commented_tickets" \
                                                                                        ".json"
            tickets_already_commented = []
            with open(already_commented_tickets_file, 'r') as json_file:
                tickets_already_commented = json.load(json_file)
            logger.logger.info("Tickets already commented for " + filter_name + ": " + str(tickets_already_commented))
    else:
        logger.logger.error("Couldn't understand.")
    pass
