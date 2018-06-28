import click
import logger
import mailer.mailer_helper as mailer_helper

# GLOBAL CONSTANTS
MAIL_OF_SHAME_TEMPLATE = "mail_of_shame.html"
WEEKLY_PROCESS_ANALYSIS_MAIL_TEMPLATE = "weekly_mail_of_tickets_process_analysis.html"


@click.command()
@click.option('--open-tickets-filter', help='Use this filter to find search tickets only given by this filter. If '
                                            'this argument is not given, it picks up default filters defined in '
                                            '/settings/jira-filters-to-scrape file.')
@click.option('--to-email-address', help='If you are testing this command, you could give your email address with '
                                         'this option and instead of actual people, you will receive the mail')
def send_mail_of_shame(open_tickets_filter, to_email_address):
    """ This command mails issues with tickets which have been marked as done without properly following the process."""
    try:
        person_task_map = mailer_helper.get_person_task_map_for_mail_of_shame(open_tickets_filter)
        template = mailer_helper.get_mail_template(MAIL_OF_SHAME_TEMPLATE)
        for assignee_email,tickets_data in person_task_map.items():
            if(not tickets_data):
                logger.logger.info(str(assignee_email)+" has completed their work properly. :-)")
                continue
            rendered_body_of_mail = template.render(name=str(tickets_data[0]['name']).strip(),
                                                    incorrectly_marked_tickets=tickets_data)
            logger.logger.info("Will be sending mail to "+assignee_email+" (unless you've used --to-email-address "
                                                                         "argument)")
            mailer_helper.send_mail(assignee_email, rendered_body_of_mail, "Mail of Shame", to_email_address)
    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()


@click.command()
@click.option('--open-tickets-filter', help='Use this filter to search within the tickets given by this filter only. If this argument is not given, it picks up default filters.')
@click.option('--to-email-address', help='The weekly email would be sent to this email address.')
@click.option('--cc-email-address', help='You can use this option to cc the mail to another email ID')
@click.option('--bcc-email-address', help='You can use this option to bcc the mail to another email ID.')
def send_weekly_analysis_mail(open_tickets_filter, to_email_address, cc_email_address, bcc_email_address):
    """ This command mails about statistics about every developer if they've followed ticket resolution process
    properly or not."""
    try:
        person_task_dict = mailer_helper.get_person_task_map_for_mail_of_shame(open_tickets_filter)
        people_who_followed_process_correctly = []
        shame_corner_people_tasks_dict = {}
        for assignee_email,tickets_data in person_task_dict.items():
            if(not tickets_data):
                people_who_followed_process_correctly.append(mailer_helper.extract_ad(assignee_email))
            else:
                shame_corner_people_tasks_dict[mailer_helper.extract_ad(assignee_email)] = tickets_data
        template = mailer_helper.get_mail_template(WEEKLY_PROCESS_ANALYSIS_MAIL_TEMPLATE)
        rendered_body_of_mail = template.render(incorrectly_marked_tickets=shame_corner_people_tasks_dict,
                                                people_who_followed_process_correctly=people_who_followed_process_correctly)
        logger.logger.info("Will be sending mail to leads (unless you've used --to-email-address "
                           "argument)")
        mailer_helper.send_mail(to_email_address, rendered_body_of_mail, "Weekly Support Tickets Process Analysis",
                                to_email_address, cc_email_address, bcc_email_address)
    except Exception as e:
        logger.logger.exception(e)
        logger.sentry_client.captureException()
