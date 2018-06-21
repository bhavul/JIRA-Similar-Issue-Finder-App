# Jira Scraper

This module takes care of scraping jira tickets. It basically reads up jira tickets and can return data. This module is used by the related_tickets_finder and mailer modules. However, it can be used on its own too.

At Endurance, this is being used to put a templated comment on all jira issues satisfying a particular JQL query.


### Directory Structure
Just like other modules, directory structure follows a standard format : 

```
/data  --------- files are populated here by the bot itself
/settings ------ Config files are put up here
__init__.py ---- so this directory gets considered as a package
commands.py ---- contains click module commands. For more info on click, check its documentation
jira_worker.py --- This contains all the core logic 
util.py -------- util methods
```

### Config Files

Following config files are necessary for the module to run properly. For each of the following files, example files (`some_config.py.example`) exist in their respective directory. You could use them to know the format for each of these files. These files have been marked to be ignored by git, so any particular server's configurations do not leak on the web.

- **jira_auth.py** : To put username, password and jira server url. Refer to `jira_auth.py.example` for format.
- **jira_filters_to_scrape.py** : To list down filters to scrape for JIRA tasks, both for building the models, as well as to find new tickets. Refer to `jira_filters_to_scrape.py.example` for format.

### Pending
More info to be added:
- How to run jira_scraper
- What commands are available
