# Related Tickets Finder

This module takes care of finding and commenting related tickets on a new JIRA ticket. 

### Directory Structure
Just like other modules, directory structure follows a standard format : 

```
/data  --------- files are populated here by the bot itself
/models -------- when you train models, model pickle files get populated here
/settings ------ Config files are put up here
__init__.py ---- so this directory gets considered as a package
commands.py ---- contains click module commands. For more info on click, check its documentation
related_tickets_finder.py --- This contains all the core logic 
util.py -------- util methods
```

### Config Files

Following config files are necessary for the module to run properly. For each of the following files, example files (`some_config.py.example`) exist in their respective directory. You could use them to know the format for each of these files. These files have been marked to be ignored by git, so any particular server's configurations do not leak on the web.

- **words_to_ignore.py** : To put words that should be ignored while building a model (if any). For format, refer to `words_to_ignore.py.example` file.
- **current_model_for_related_tickets.py** : This lists the model that would be used by the bot by default to find related tickets and comment them in the new tickets. Let it be empty right now since you might not have a model to start with.  
Refer to `current_model_for_related_tickets.py.example` for format.


## Steps to follow to make it work for your company

So, now that you understand how to work with different commands for this bot, here are the steps.

1. **Make sure to create required config files with correct data.**. 
2. **Train a model**  
`python app_cli.py comment_related_tickets train_related_tickets_model`
3. **Add the trained model's name in current_model_for_related_tickets.py file**.  
The model's pickle file would have gotten saved in `<Project-Dir>/related_tickets_finder/models/` directory
4. **Run the bot to comment related tickets**  
`python app_cli.py related_ticket_finder comment_related_tickets`



### Pending
More info to be added:
- How to run related tickets finder
- Detailed info for what commands are available



