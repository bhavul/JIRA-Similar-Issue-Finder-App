import os
import logger
import json
import configparser

from common_util import project_dir_path


#constant
THIS_MODULE_DIRECTORY = os.path.join(project_dir_path, 'related_tickets_finder')
CONFIG_DIRECTORY = os.path.join(THIS_MODULE_DIRECTORY, 'settings')

jql_filters = configparser.ConfigParser()
jql_filters_config_file = os.path.join(CONFIG_DIRECTORY,'jql_filters_to_scrape.config')
jql_filters.read(jql_filters_config_file)
model_config = configparser.ConfigParser()
model_config_file = os.path.join(CONFIG_DIRECTORY,'current_model_in_use.config')
model_config.read(model_config_file)


def create_already_commented_tickets_file_if_not_exists(filename):
    if not os.path.exists(filename):
        logger.logger.warning("No already existing file with already commented tickets data.")
        list_of_str = ['WSE-123456']
        json.dump(list_of_str, open(filename, "w"))

def get_model_file_path(filter_name, test_model_name):
    model_path_dir = os.path.join(THIS_MODULE_DIRECTORY,'models')
    model_dict = dict(model_config['FILTER_MODEL_MAP'])
    if(filter_name == 'custom'):
        if test_model_name is not None:
            model_path = os.path.join(model_path_dir,test_model_name)
        else:
            raise Exception("For custom filter, a model name must be given to know which model to use.")
    elif(filter_name in dict(jql_filters['FILTER_OPEN_NEW_TICKETS']).keys()):
        model_path = os.path.join(model_path_dir,model_dict[filter_name])
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