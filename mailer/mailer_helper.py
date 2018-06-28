import logger
import re
from email.mime.text import MIMEText
import smtplib
from email.mime.multipart import MIMEMultipart
from fuzzywuzzy import fuzz
import jira_scraper.settings.jira_auth as auth
from pprint import pformat
import jira_scraper.jira_worker as scraper
import mailer.settings.bot_gmail_auth as gmail_auth
import mailer.settings.jira_filters_to_scrape as jira_filters
import jinja2
from util import project_dir_path

# Constants
REGEX_TO_FETCH_PANELS = r"({panel:title=[\w\s]*[^A-Za-z0-9]*[\w\s]*\?*}[\w\s.&,`\"\\\d/$&+,:;=?@#|'<>.^*()%!-]*{panel})"
REGEX_TO_FETCH_TEXT_INSIDE_PANELS = r"{panel:title=[\w\s]*[^A-Za-z0-9]*[\w\s]*\?*}([\w\s.&,`\"\\\d/$&+,:;=?@#|'<>.^*()%!-]*){panel}"
LIST_OF_TEXT_THAT_MEANS_YES = ['yes', 'yup', 'yeah', 'yea', 'ya', 'yes.', 'yes,', 'yes!', 'yo!', 'yo', 'yup!', 'yeah!', 'yeah.']

# Email Constants
fromaddr = gmail_auth.name+" <"+gmail_auth.email+">"
fromemailaddr = gmail_auth.email
bot_mail_password = gmail_auth.password


# todo (high) - improve the logic of checking the linked ticket - shuold be a tech debt item!
def find_if_task_linked(ticket):
    logger.logger.info("The ticket has "+str(len(ticket['linked_issues_data']))+" linked issues.")
    if(len(ticket['linked_issues_data']) > 0):
        return True
    return False

# todo (low) - this feature is highly coupled to what endurance needed. Maybe we can customize this.
def find_if_issue_is_recurring(comment):
    panel_texts = re.findall(REGEX_TO_FETCH_PANELS,comment['body'])
    if not panel_texts:
        return False
    else:
        for panel_text_individual in panel_texts:
            if('can it occur again' in panel_text_individual.lower()):
                logger.logger.debug(panel_text_individual)
                answer = re.findall(REGEX_TO_FETCH_TEXT_INSIDE_PANELS, panel_text_individual)
                answer = [ans.strip() for ans in answer]
                answer = answer[0]
                logger.logger.debug("answer : "+str(answer))
                if(answer.lower() in LIST_OF_TEXT_THAT_MEANS_YES):
                    return True
                else:
                    return False
                    # todo - add check for frequency of ticket. Count as recurring only if highly frequent.
        else:
            logger.logger.error(panel_texts)
            logger.logger.error("THIS IS A PROBLEM! THIS SHOULDN'T HAPPEN!")
            return False

def send_mail(default_to_email_addr, rendered_body_of_mail, mail_subject, custom_to_email_address,
              cc_email_address=None,
              bcc_email_address=None):
    toaddr = default_to_email_addr
    if custom_to_email_address is not None:
        toaddr = custom_to_email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    if cc_email_address:
        msg['Cc'] = cc_email_address
    if bcc_email_address:
        msg['Bcc'] = bcc_email_address
    msg['Subject'] = mail_subject
    msg.attach(MIMEText(rendered_body_of_mail, 'html'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromemailaddr, bot_mail_password)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


def has_assignee_edited_comment(comment):
    panel_texts = re.findall(REGEX_TO_FETCH_PANELS,comment['body'])
    if not panel_texts:
        return True
    else:
        for index,question in enumerate(panel_texts):
            logger.logger.debug(question)
            answer = re.findall(REGEX_TO_FETCH_TEXT_INSIDE_PANELS, question)
            answer = [ans.strip() for ans in answer]
            answer = answer[0]
            logger.logger.debug("answer : "+str(answer))
            # todo (med) : the values we're checking for (RHS) should be same as ones defined in templated commentor
            # todo (med) : in a separate config file
            if(index == 0):
                duplication_value = fuzz.ratio(answer,'Fill your answer here.')
                logger.logger.debug("question:1 | duplication_value:"+str(duplication_value))
                if(duplication_value > 85):
                    return False
            elif(index == 1):
                duplication_value = fuzz.ratio(answer,'Fill your answer here. You can put a link to confluence page where the issue & its solution has been described, or describe the way you debugged and solved this issue. Extra marks for clean formatting.')
                logger.logger.debug("question:2 | duplication_value:"+str(duplication_value))
                if(duplication_value > 85):
                    return False
            elif(index == 2):
                duplication_value = fuzz.ratio(answer,"Change this line to JUST SAY 'Yes' or 'No'. Yes means that ticket is not just recurring but has a possible permanent fix / automation that we could do. If it's those tickets which can be recurring but can not be automated, say 'No'. Remember, if you say, 'Yes', then make sure to create a Tech Debt task and link it to this ticket before you close this.")
                logger.logger.debug("question:3 | duplication_value:"+str(duplication_value))
                if(duplication_value > 85):
                    return False
        else:
            logger.logger.info(panel_texts)
            return True
    pass


def get_data_for_mail_of_shame(filter_to_use, jira_obj, person_task_map):
    for filter_name, filter in filter_to_use.items():
        logger.logger.info("Crawling data for "+str(filter_name))
        jira_tickets_corpus = scraper.filter_crawler(jira_obj, filter, True)
        logger.logger.info("Crawling done.")
        for ticket in jira_tickets_corpus:
            logger.logger.info("Will check for mis-documentation for ticket : "+str(ticket['jiraid']))
            if ticket['assigneeEmail'] not in person_task_map:
                person_task_map[ticket['assigneeEmail']] = []
            if ticket['comments_data']:
                for comment in ticket['comments_data']:
                    if comment['name'] == auth.jira_username:
                        jiraid_list = [ticket_with_issue['jiraid'] for ticket_with_issue in person_task_map[ticket[
                            'assigneeEmail']]]
                        if(ticket['jiraid'] in jiraid_list):
                            # to escape case of duplicate comments by jira bot when we've alrdy taken data
                            continue
                        is_not_lazy_person = has_assignee_edited_comment(comment)
                        if(not is_not_lazy_person):
                            issue = "Did not properly document what was done to solve the ticket."
                            person_task_map[ticket['assigneeEmail']].append({
                                'url': auth.jira_url + "/browse/" + ticket['jiraid'],
                                'name':ticket['assigneeName'],
                                'jiraid':ticket['jiraid'],
                                'title': ticket['title'],
                                'issue': issue})
                            continue
                        is_recurring = find_if_issue_is_recurring(comment)
                        if (is_recurring):
                            logger.logger.info("Found recurring issue!")
                            is_task_linked = find_if_task_linked(ticket)
                            if (not is_task_linked):
                                person_task_map[ticket['assigneeEmail']].append({
                                    'url': auth.jira_url + "/browse/" + ticket['jiraid'],
                                    'name':ticket['assigneeName'],
                                    'jiraid':ticket['jiraid'],
                                    'title': ticket['title'],
                                    'issue': "Ticket is recurring but no tech-debt task created/linked to it."})
            else:
                logger.logger.warning(str(ticket["jiraid"])+" has no comments!")
    logger.logger.info("Person - Task Map:" + pformat(person_task_map))

def get_person_task_map_for_mail_of_shame(open_tickets_filter):
    jira_obj = scraper.connect_to_jira()
    default_filters = jira_filters.filters_to_get_completed_tickets
    if open_tickets_filter is not None:
        filter_to_use = {'custom': open_tickets_filter}
    else:
        filter_to_use = default_filters
    logger.logger.info("Filter I'm using : " + pformat(filter_to_use))
    person_task_map = {}
    get_data_for_mail_of_shame(filter_to_use, jira_obj, person_task_map)
    return person_task_map

def extract_ad(assignee_email):
    """This takes in email-id and spits out the username of the email."""
    return assignee_email.split('@')[0]

def get_mail_template(template_file_name):
    templateLoader = jinja2.FileSystemLoader(searchpath=project_dir_path+"/mailer/templates/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_file_name)
    return template