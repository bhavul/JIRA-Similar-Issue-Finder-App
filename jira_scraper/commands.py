import click
import logger
import jira_scraper.settings.jira_filters_to_scrape as jira_filters
import jira_scraper.util as jira_scraper_pkg_util
from util import project_dir_path
import json
import jira_scraper.jira_worker as scraper
from pprint import pformat

@click.command()
@click.option('--open-tickets-filter', help='If this argument is given, it picks up the tasks that satisfy this '
                                            'filter instead of default filters.')
def post_template_comment_on_new_tickets(open_tickets_filter):
    """This creates a template comment on each ticket which needs to be filled by a developer before the ticket is
    marked as completed."""
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
                                             "/jira_scraper/data/"+filter_name+"_already_commented_template_tickets" \
                                                                               ".json"
            jira_scraper_pkg_util.create_already_commented_tickets_file_if_not_exists(already_commented_tickets_file)
            with open(already_commented_tickets_file, 'r') as data_file:
                tickets_already_commented = json.load(data_file)
            new_tickets_corpus = [ticket for ticket in jira_tickets_corpus if ticket['jiraid'] not in tickets_already_commented]
            if not new_tickets_corpus:
                logger.logger.info("No new tickets to comment on from " + filter_name + ". Moving on to next filter.")
                continue
            for ticket in new_tickets_corpus:
                scraper.comment_on_task(jira_obj, ticket['jiraid'], jira_scraper_pkg_util.get_template_comment())
                tickets_already_commented.append(ticket['jiraid'])
            with open(already_commented_tickets_file,'w') as outfile:
                json.dump(tickets_already_commented, outfile)
            logger.logger.info("Done for " + str(filter_name))
        logger.logger.info("Execution completed.")
    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()