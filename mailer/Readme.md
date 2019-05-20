# Mailer

This module takes care of triggering different mails to developers, leads regarding data related to tickets. 

At Endurance, this was being used to send a mail of shame every day to the developer who closed/resolved a ticket on JIRA without following the process of commenting what the issue was and how they solved it. Essentially mail of shame code could be used as a template for any other similar mails to monitor if a process is being followed properly.


### Directory Structure
Just like other modules, directory structure follows a standard format : 

```
/data  --------- files are populated here by the bot itself
/settings ------ Config files are put up here
/templates ----- html of mails are put up here
__init__.py ---- so this directory gets considered as a package
commands.py ---- contains click module commands. For more info on click, check its documentation
mailer_helper.py --- This contains all the core logic 
```

### Config Files

Following config files are necessary for the module to run properly. For each of the following files, example files (`some_config.py.example`) exist in their respective directory. You could use them to know the format for each of these files. These files have been marked to be ignored by git, so any particular server's configurations do not leak on the web.

- **bot_gmail_auth.py** : This houses the gmail credentials for the bot. Refer to `bot_gmail_auth.py.example` for format.
- **jira_filters_to_scrape.py** : To list down filters to scrape for JIRA tasks, for mailing. Refer to `jira_filters_to_scrape.py.example` for format.


### How to run

In most cases, you just need to run : 
```bash
python app_cli.py mailer send_mail_of_shame
```
This will find the jira tickets on which process is not followed properly and send mails to the assignee of such tickets automatically. 

If you wish to send all the mails of shame to a specific email ID only (for testing purposes, or if you're a lead), then command looks like : 
```bash
python app_cli.py mailer send_mail_of_shame --to-email-address your_email@gmail.com
```

Of course, you can always check all the arguments and possible values by running : 

```bash
python app_cli.py mailer send_mail_of_shame --help
```

### Pending
More info to be added:
- How to run mailer
- What commands are available
