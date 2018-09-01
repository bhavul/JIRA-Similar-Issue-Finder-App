import sys

import click
import os

# Add current path to sys path so, imports work nicely
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import jira_template_commentor.commands as jira_template_commentor
import related_tickets_finder.commands as related_ticket_finder_commands
import mailer.commands as mailer_commands

__author__ = "Bhavul Gauri"


@click.group()
def cli():
    """ This is a JIRA Bot written by Bhavul which is supposed to help devs in various ways. Check the commands
    listed below to know what all actions the bot can perform."""
    pass


@cli.group()
def related_ticket_finder():
    """The commands here can be used to train a TF-IDF model and/or use the model to comment related tickets for
    filters defined."""
    pass


@cli.group()
def jira_scraper_commentor():
    """The commands here are used to scrape different forms of jira data and then return them or comment on them."""
    pass


@cli.group()
def mailer():
    """The commands here are used to send different monitoring mails to developers and/or leads."""
    pass


related_ticket_finder.add_command(related_ticket_finder_commands.train_related_tickets_model)
related_ticket_finder.add_command(related_ticket_finder_commands.comment_related_tickets)
related_ticket_finder.add_command(related_ticket_finder_commands.get_data)
jira_scraper_commentor.add_command(jira_template_commentor.post_template_comment_on_new_tickets)
mailer.add_command(mailer_commands.send_mail_of_shame)
mailer.add_command(mailer_commands.send_weekly_analysis_mail)

if __name__ == "__main__":
    cli()
