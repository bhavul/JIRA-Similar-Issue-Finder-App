# Jira Template Commentor

At Endurance, this was being used to put a templated comment on all jira issues satisfying a particular JQL query.

### Directory Structure
Just like other modules, directory structure follows a standard format : 

```
/data  --------- files are populated here by the bot itself
/settings ------ Config files are put up here
__init__.py ---- so this directory gets considered as a package
commands.py ---- contains click module commands. For more info on click, check its documentation
util.py -------- util methods
```

### Config Files

Following config files are necessary for the module to run properly. For each of the following files, example files (`some_config.py.example`) exist in their respective directory. You could use them to know the format for each of these files. These files have been marked to be ignored by git, so any particular server's configurations do not leak on the web.

- **jira_filters_to_scrape.py** : To list down filters to scrape for JIRA tasks, both for building the models, as well as to find new tickets. Refer to `jira_filters_to_scrape.py.example` for format.

### How to run

Once you have filled the config files correctly, ideally you'll just need to run : 

```bash
python app_cli.py jira_scraper_commentor post_template_comment_on_new_tickets
```

If you need to test this feature on a custom JQL query, you could use `--open-tickets-filter` argument like this : 

```bash
python app_cli.py jira_scraper_commentor post_template_comment_on_new_tickets --open-tickets-filter "project = ABC AND key = ABC-2494"
```
This would just post the comment in ABC-2494. 

Of course, you can check for all supported arguments and options by :

```bash
python app_cli.py jira_scraper_commentor post_template_comment_on_new_tickets --help
```

