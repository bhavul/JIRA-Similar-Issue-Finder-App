import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath('jira_bot.py'))))
import scripts.settings.jira_filters_to_scrape as jira_filters
import scripts.jira_worker as scraper
import scripts.related_tickets_finder as related_tickets_finder
import pickle
import scripts.settings.current_model_for_related_tickets as current_model
import click
import scripts.logger as logger
from pprint import pformat
import os.path
import schedule
import time

__author__ = "Bhavul Gauri"

## TODO
# 1. Sort by date
# 2. Change jira_auth.py to config file. use configparser. For filters to scrape also do same. For words to ignore also.
# 3. words-to-ignore --- if file exists only then use it. else take all.
# 4. make cronjob a better feature and then document about cronjob.


@click.group()
def cli():
    """ This is a JIRA Bot written by Bhavul which is supposed to help devs with tickets. """
    pass

@cli.command()
def train_related_tickets_model():
    """This runs a script to train model on all closed tickets"""
    try:
        jira_obj = scraper.connect_to_jira()
        for filter_name,filter in jira_filters.filters_to_get_completed_tickets.items():
            logger.logger.info("Will crawl "+filter_name)
            jira_tickets_corpus = scraper.filter_crawler(jira_obj,filter)
            logger.logger.info("Crawling of "+filter_name+" done.")
            related_tickets_finder.train_and_save_tfidf_model(jira_tickets_corpus, "model_"+filter_name)
    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()


def get_model_file_path(filter_name, test_model_name):
    model_path = './models/'
    if(filter_name == 'custom'):
        if test_model_name is not None:
            model_path += test_model_name
        else:
            raise Exception("For custom filter, a model name must be given to know which model to use.")
    elif(filter_name == 'open_fnb'):
        model_path += current_model.models['fnb']
    elif(filter_name == 'open_cp'):
        model_path += current_model.models['cp']
    else:
        raise Exception("filter name seems to be wrong.")
    logger.logger.info("Model being used - "+model_path)
    return model_path


def get_formatted_comment(list_of_related_jira_ids):
    comment = "*Here are few old and completed tickets which seemed similar to me (in no particular order) :* "
    for ticket_id in list_of_related_jira_ids:
        comment += '['+str(ticket_id)+'|'+'https://jira.endurance.com/browse/'+str(ticket_id)+'], '
    comment = comment.rstrip(', ')
    comment += '\n\nYou could check the code changes / queries / comments that were done in these tickets. Maybe they might ' \
               'help. :-)'
    return comment


@cli.command()
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
        logger.logger.info("Filter I'm using : "+pformat(filter_to_use))
        for filter_name,filter in filter_to_use.items():
            jira_tickets_corpus = scraper.filter_crawler(jira_obj,filter)
            already_commented_tickets_file = "./data/"+filter_name+"_already_commented_tickets.pickle"
            create_already_commented_tickets_file_if_not_exists(already_commented_tickets_file)
            with open(already_commented_tickets_file, 'rb') as pickled_file:
                tickets_already_commented = pickle.load(pickled_file)
            new_tickets_corpus = [ticket for ticket in jira_tickets_corpus if ticket['jiraid'] not in tickets_already_commented]
            if not new_tickets_corpus:
                logger.logger.info("No new tickets to comment on from "+filter_name+". Moving on to next filter.")
                continue
            model_file_path = get_model_file_path(filter_name, test_model)
            related_tickets_data = related_tickets_finder.find_top_n_related_jira_tickets(5,new_tickets_corpus,model_file_path)
            for ticket in related_tickets_data:
                logger.logger.info("Ticket:"+ticket['jiraid']+"| Related tickets:"+str(ticket['related_tickets']))
                scraper.comment_on_task(jira_obj, ticket['jiraid'], get_formatted_comment(ticket['related_tickets']))
                tickets_already_commented.append(ticket['jiraid'])
                # break;
            logger.logger.info(tickets_already_commented)
            pickle.dump(tickets_already_commented, open(already_commented_tickets_file, "wb"))
            logger.logger.info("Done for "+str(filter_name))
        logger.logger.info("Execution completed.")
    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()

@cli.command()
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
            already_commented_tickets_file = "./data/"+filter_name+"_already_commented_tickets.pickle"
            tickets_already_commented = []
            with open(already_commented_tickets_file, 'rb') as pickled_file:
                tickets_already_commented = pickle.load(pickled_file)
            logger.logger.info("Tickets already commented for "+filter_name+": "+str(tickets_already_commented))
    else:
        logger.logger.error("Couldn't understand.")
    pass

def create_already_commented_tickets_file_if_not_exists(filename):
    if not os.path.exists(filename):
        logger.logger.warning("No already existing file with already commented tickets data.")
        list_of_str = ['WSE-123456']
        pickle.dump(list_of_str, open(filename, "wb"))

def test_text():
    logger.logger.info("I'm working...")

schedule.every(1).minutes.do(test_text)

@cli.command()
def cronjob():
    while 1:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    cli()



