# Jira Scraper

This module takes care of scraping jira tickets. It basically reads up jira tickets and can return data. This module is used by all the other modules (related_tickets_finder ,mailer, etc). 




### Directory Structure
Just like other modules, directory structure follows a standard format : 

```
/settings ------ Config files are put up here
__init__.py ---- so this directory gets considered as a package
jira_worker.py --- This contains all the core logic 
```

### Config Files

Following config files are necessary for the module to run properly. For each of the following files, example files (`some_config.py.example`) exist in their respective directory. You could use them to know the format for each of these files. These files have been marked to be ignored by git, so any particular server's configurations do not leak on the web.

- **jira_auth.py** : To put username, password and jira server url. Refer to `jira_auth.py.example` for format.
- **jira_filters_to_scrape.py** : To list down filters to scrape for JIRA tasks, both for building the models, as well as to find new tickets. Refer to `jira_filters_to_scrape.py.example` for format.


### Pending
More info to be added:
- How to run jira_scraper
- What commands are available
