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
import time
import json
from scripts.util import project_dir_path

__author__ = "Bhavul Gauri"

## TODO
# 1. Sort by date
# 2. Change jira_auth.py to config file. use configparser. For filters to scrape also do same. For words to ignore also.
# 3. words-to-ignore --- if file exists only then use it. else take all.
# 4. make cronjob a better feature and then document about cronjob.
# 6. mail whoever doesn't fill in comments
# 7. mail about data of the month for tickets
# 8. mail about tech debt tasks just before sprint planning.


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
    model_path = project_dir_path+'/scripts/models/'
    if(filter_name == 'custom'):
        if test_model_name is not None:
            model_path += test_model_name
        else:
            raise Exception("For custom filter, a model name must be given to know which model to use.")
    elif(filter_name in jira_filters.filters_to_get_new_tickets.keys()):
        model_path += current_model.models[filter_name]
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
            already_commented_tickets_file = project_dir_path + \
                                             "/scripts/data/"+filter_name+"_already_commented_tickets.json"
            create_already_commented_tickets_file_if_not_exists(already_commented_tickets_file)
            with open(already_commented_tickets_file, 'r') as data_file:
                tickets_already_commented = json.load(data_file)
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
            with open(already_commented_tickets_file,'w') as outfile:
                json.dump(tickets_already_commented, outfile)
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
            already_commented_tickets_file = project_dir_path + \
                                             "/scripts/data/"+filter_name+"_already_commented_tickets.json"
            tickets_already_commented = []
            with open(already_commented_tickets_file, 'r') as json_file:
                tickets_already_commented = json.load(json_file)
            logger.logger.info("Tickets already commented for "+filter_name+": "+str(tickets_already_commented))
    else:
        logger.logger.error("Couldn't understand.")
    pass

def create_already_commented_tickets_file_if_not_exists(filename):
    if not os.path.exists(filename):
        logger.logger.warning("No already existing file with already commented tickets data.")
        list_of_str = ['WSE-123456']
        json.dump(list_of_str, open(filename, "w"))


def get_template_comment():
    comment = "{color:#d04437}*Hello!*{color} \n\n If you're the rockstar who will close this ticket, then please edit this comment, fill the answers to questions below and only then close it."
    comment += "\n \\\\"
    comment += '{panel:title=What was the issue?} \n Fill your answer here. \n {panel}'
    comment += '{panel:title=How did you solve it?} \n Fill your answer here. You can put a link to confluence page where the issue & its solution has been described, or describe the way you debugged and solved this issue. Extra marks for clean formatting.\n {panel}'
    comment += '{panel:title=Can it occur again in the future AND have a permanent fix possible?} \n Change this line to JUST SAY \'Yes\' or \'No\'. Yes means that ticket is not just recurring but has a possible permanent fix / automation that we could do. If it\'s those tickets which can be recurring but can not be automated, say \'No\'. Remember, if you say, \'Yes\', then make sure to create a Tech Debt task and link it to this ticket before you close this. \n {panel}'
    comment += '{panel:title=If recurring and fixable, how frequent can this sort of ticket be?} Edit this line to say one of the following - Every Day, Every Week, Bi-weekly, Every month, Once in a few months, Once in 5-6 months, Once in a year.{panel}\n\n\n'
    comment += "----"
    comment += '\n{color:#707070}_Time is the most precious gift you could give to somebody. By filling this ' \
               'properly, ' \
               'you would do just that for somebody who might come lurking to this ticket in the future to check how ' \
               'it was solved. Thanks!_{color}'
    return comment


@cli.command()
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
        logger.logger.info("Filter I'm using : "+pformat(filter_to_use))
        for filter_name,filter in filter_to_use.items():
            jira_tickets_corpus = scraper.filter_crawler(jira_obj,filter)
            already_commented_tickets_file = project_dir_path + \
                                             "/scripts/data/"+filter_name+"_already_commented_template_tickets.json"
            create_already_commented_tickets_file_if_not_exists(already_commented_tickets_file)
            with open(already_commented_tickets_file, 'r') as data_file:
                tickets_already_commented = json.load(data_file)
            new_tickets_corpus = [ticket for ticket in jira_tickets_corpus if ticket['jiraid'] not in tickets_already_commented]
            if not new_tickets_corpus:
                logger.logger.info("No new tickets to comment on from "+filter_name+". Moving on to next filter.")
                continue
            for ticket in new_tickets_corpus:
                scraper.comment_on_task(jira_obj, ticket['jiraid'], get_template_comment())
                tickets_already_commented.append(ticket['jiraid'])
            with open(already_commented_tickets_file,'w') as outfile:
                json.dump(tickets_already_commented, outfile)
            logger.logger.info("Done for "+str(filter_name))
        logger.logger.info("Execution completed.")
    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()


if __name__ == "__main__":
    cli()



