import os
import logger
import json

# todo (med) - this method is duplicated in util module of related_tickets_finder package. Needs de-dup.
def create_already_commented_tickets_file_if_not_exists(filename):
    if not os.path.exists(filename):
        logger.logger.warning("No already existing file with already commented tickets data.")
        list_of_str = ['WSE-123456']
        json.dump(list_of_str, open(filename, "w"))

# todo (low) - this could be moved to a html or a better template format?
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