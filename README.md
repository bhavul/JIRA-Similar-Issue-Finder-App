# JIRA Similar Tickets Finder Bot

This is a side-project I did for improving JIRA SLAs at Endurance International Group. It essentially comments related past JIRA tickets on the new JIRA support tickets that get escalated to a developer. 

This helps the developer to get the context of what piece of codebase to look at, what tables to look at, and in general get an idea of what needs to be debugged by looking at old completed similar tickets.

# Installation

You require Python v3. I used Python v3.5 to create this and it runs fine on it. If you find issues with other versions of Python v3, please report it.

There are quite a few dependencies, all listed in requirements.txt file. So, once you have python v3, just run the following command :

`pip install -r requirements.txt`

Once they're all installed, you can use the bot! 

# How to use?

Thanks to [click](https://dbader.org/blog/python-commandline-tools-with-click#intro), you can actually get to know this without even reading this section. 

Just run `python jira_bot.py --help`

It should present with you a guide : 

```bash
Usage: jira_bot.py [OPTIONS] COMMAND [ARGS]...

  This is a JIRA Bot written by Bhavul which is supposed to help devs with
  tickets.

Options:
  --help  Show this message and exit.

Commands:
  comment_related_tickets      This runs a script to comment related
                               tickets...
  get_data                     This command returns data that is being used...
  train_related_tickets_model  This runs a script to train model on all...
```

There are 3 commands available. 
1. comment_related_tickets
2. get_data
3. train_related_tickets_model

You could ask the program for help regarding each of those commands too. 

For example, 
`python jira_bot.py comment_related_tickets --help` would return you : 

```bash
Usage: jira_bot.py comment_related_tickets [OPTIONS]

  This runs a script to comment related tickets on each new ticket for
  configured filters

Options:
  --test-model TEXT           Find related tickets for given model.
  --open-tickets-filter TEXT  Use this filter to find related tickets to
                              tickets given by this filter. Please provide
                              test-model also if you pass a value for this
                              arg. If this argument is not given, it picks up
                              default filters.
  --help                      Show this message and exit.
```

Suggesting, that `comment_related_tickets` can take `--test-model` and/or `--open-tickets-filter`
option. These parameters let you comment related tickets by using a custom model (whose path you give as the argument) AND/OR by using a different filter to get open-tickets. 

For example, if I had experimented to build a new model called *'MojoJojoModel'*, and I wanted to only use that model to comment only on two JIRAs - WSE-1234, and WSE-2345. Then I could run the bot like this : 

**`python jira_bot.py comment_related_tickets --test-model "/Users/bhavul.g/JiraSimilarityHelper/models/MojoJojo" --open-tickets-filter "project = WSE AND key in (WSE-1234, WSE-2345)"`**

Of course, since `--test-model` and `--open-tickets-filter` are each an **option**, so if you don't give them, it would still run. It would pick up the models defined in file **current_model_for_related_tickets.py**, and pick up the filters from **jira_filters_to_scrape.py** file. 


## Steps to follow to make it work for your company

So, now that you understand how to work with different commands for this bot, here are the steps.

1. **Make sure to create required files with correct data.** For each of the following files, examples file exist in their respective directory. You could use them to know the format for each of these files. These files have been marked to be ignored by git, so any particular server's configurations do not leak on the web.
    - **jira_auth.py** : To put username, password and jira server url
    - **words_to_ignore.py** : To put words that should be ignored while building a model (if any)
    - **jira_filters_to_scrape.py** : To list down filters to scrape for JIRA tasks, both for building the models, as well as to find new tickets.
    - **current_model_for_related_tickets.py** : This lists the model that would be used by the bot by default to find related tickets and comment them in the new tickets. Let it be empty right now since you might not have a model to start with.
x
2. **Train a model**
`python jira_bot.py train_related_tickets_model`
3. **Add the trained model's name in current_model_for_related_tickets.py file**. The model's pickle file would have gotten saved in `<Project-Dir>/scripts/models/` directory
4. **Run the bot to comment related tickets**

`python jira_bot.py comment_related_tickets`


# Can I have this feature?

Let's talk about it. If you can develop yourself, then go ahead, fork the repo and do it. If you think it would help all, then kindly raise a PR, and I'd love to merge it.


# Author

Bhavul Gauri