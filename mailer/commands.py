import click
import logger
import jira_scraper.jira_worker as scraper
import mailer.settings.jira_filters_to_scrape as jira_filters
from pprint import pformat
import mailer.mailer_helper as mailer_helper
from util import project_dir_path
import jinja2

# GLOBALS
templateLoader = jinja2.FileSystemLoader(searchpath=project_dir_path+"/mailer/templates/")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "mail_of_shame.html"
template = templateEnv.get_template(TEMPLATE_FILE)

@click.command()
@click.option('--open-tickets-filter', help='Use this filter to find related tickets to tickets given by this filter. Please provide test-model also if you pass a value for this arg. If this argument is not given, it picks up default filters.')
@click.option('--to-email-address', help='If you are testing this command, you could give your email address with '
                                         'this option and regardless of who did not follow process properly, '
                                         'you will get their emails as well')
def send_mail_of_shame(open_tickets_filter, to_email_address):
    """ This command mails issues with tickets which have been marked as done without properly following the process."""
    try:
        jira_obj = scraper.connect_to_jira()
        default_filters = jira_filters.filters_to_get_completed_tickets
        if open_tickets_filter is not None:
            filter_to_use = {'custom':open_tickets_filter}
        else:
            filter_to_use = default_filters
        logger.logger.info("Filter I'm using : " + pformat(filter_to_use))
        person_task_map = {}
        mailer_helper.get_data_for_mail_of_shame(filter_to_use, jira_obj, person_task_map)
        for assignee_email,tickets_data in person_task_map.items():
            if(not tickets_data):
                logger.logger.info(str(assignee_email)+" has completed their work properly. :-)")
                continue
            rendered_body_of_mail = template.render(name=str(tickets_data[0]['name']).strip(),
                                                    incorrectly_marked_tickets=tickets_data)
            logger.logger.info("Will be sending mail to "+assignee_email+" (unless you've used --to-email-address "
                                                                         "argument)")
            mailer_helper.send_mail(assignee_email, rendered_body_of_mail, to_email_address)
    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()


