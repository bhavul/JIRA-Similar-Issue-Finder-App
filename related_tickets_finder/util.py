import os
import logger
import json
from util import project_dir_path
import jira_scraper.settings.jira_filters_to_scrape as jira_filters
import related_tickets_finder.settings.current_model_for_related_tickets as current_model

def create_already_commented_tickets_file_if_not_exists(filename):
    if not os.path.exists(filename):
        logger.logger.warning("No already existing file with already commented tickets data.")
        list_of_str = ['WSE-123456']
        json.dump(list_of_str, open(filename, "w"))

def get_model_file_path(filter_name, test_model_name):
    model_path = project_dir_path+'/related_tickets_finder/models/'
    if(filter_name == 'custom'):
        if test_model_name is not None:
            model_path += test_model_name
        else:
            raise Exception("For custom filter, a model name must be given to know which model to use.")
    elif(filter_name in jira_filters.filters_to_get_new_tickets.keys()):
        model_path += current_model.models[filter_name]
    else:
        raise Exception("filter name seems to be wrong.")
    logger.logger.info("Model being used - " + model_path)
    return model_path

# todo - move to a template which is configurable.
def get_formatted_comment(list_of_related_jira_ids):
    comment = "*Here are few old and completed tickets which seemed similar to me (in no particular order) :* "
    for ticket_id in list_of_related_jira_ids:
        comment += '['+str(ticket_id)+'|'+'https://jira.endurance.com/browse/'+str(ticket_id)+'], '
    comment = comment.rstrip(', ')
    comment += '\n\nYou could check the code changes / queries / comments that were done in these tickets. Maybe they might ' \
               'help. :-)'
    return comment