import json
from pprint import pformat
import click
import jira_scraper.jira_worker as scraper
import jira_template_commentor.util as jira_template_commentor_util
import logger
from common_util import project_dir_path
import os
import configparser

#constant
THIS_MODULE_DIRECTORY = os.path.join(project_dir_path, 'jira_template_commentor')

@click.command()
@click.option('--open-tickets-filter', help='If this argument is given, it picks up the tasks that satisfy this '
                                            'filter instead of default filters.')
def post_template_comment_on_new_tickets(open_tickets_filter):
    """This creates a template comment on each ticket which needs to be filled by a developer before the ticket is
    marked as completed."""
    try:
        jira_obj = scraper.connect_to_jira()

        # read jql filters config
        jql_filters = configparser.ConfigParser()
        jql_filters_config_file = os.path.join(os.path.join(THIS_MODULE_DIRECTORY, 'settings'), 'jira_jql_filters.config')
        jql_filters.read(jql_filters_config_file)
        default_filters = dict(jql_filters['FILTERS_FOR_TRAINING_MODEL'])
        logger.logger.info("Loaded default filters")

        # finalize which filter to be used
        if open_tickets_filter is not None:
            filter_to_use = {'custom': open_tickets_filter}
        else:
            filter_to_use = default_filters
        logger.logger.info("Filter I'm using : " + pformat(filter_to_use))

        # crawl filter and post templated comments
        for filter_name, filter_query in filter_to_use.items():
            # scrape every ticket in filter
            jira_tickets_corpus = scraper.filter_crawler(jira_obj, filter_query)

            # find jira tickets on which already commented the template comment
            already_commented_tickets_file = os.path.join(os.path.join(THIS_MODULE_DIRECTORY, 'data'),
                                                          filter_name+'_already_commented_template_tickets.json')
            jira_template_commentor_util.create_already_commented_tickets_file_if_not_exists(already_commented_tickets_file)
            with open(already_commented_tickets_file, 'r') as data_file:
                tickets_already_commented = json.load(data_file)

            # Get only those tickets which do not have templated comment
            new_tickets_corpus = [ticket for ticket in jira_tickets_corpus if
                                  ticket['jiraid'] not in tickets_already_commented]
            if not new_tickets_corpus:
                logger.logger.info("No new tickets to comment on from " + filter_name + ". Moving on to next filter.")
                continue

            # post template comment.
            templated_comment = jira_template_commentor_util.get_template_comment()
            for ticket in new_tickets_corpus:
                scraper.comment_on_task(jira_obj, ticket['jiraid'], templated_comment)
                tickets_already_commented.append(ticket['jiraid'])

            # update the already commented file with new jira IDs
            with open(already_commented_tickets_file, 'w') as outfile:
                json.dump(tickets_already_commented, outfile)

            logger.logger.info("Done for " + str(filter_name))
        logger.logger.info("Execution completed.")
    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()
