# JIRA Helper Bot

This is a side-project I did for improving JIRA SLAs at Endurance International Group while I was working with them. It started with commenting related past JIRA tickets on the new JIRA support tickets that get escalated to a developer. 

This helps the developer to get the context of what piece of codebase to look at, what tables to look at, and in general get an idea of what needs to be debugged by looking at old completed similar tickets.

However, now it supports multiple features:
1. Send mails to developers who close tickets without following a process put in place (Mail of Shame)
2. Can scrape jira data for whatever purpose necessary
3. Comments related tickets

Further, more features would keep on getting added. The idea is to use data in JIRA and help out in making processes more efficient, cheaper and faster.

It can be used by any team across the globe who uses JIRA, and is especially helpful if you folks have support tickets being raised as JIRA tickets.

# Installation

You require Python v3. I used Python v3.5 to create this and it runs fine on it. If you find issues with other versions of Python v3, please report it.

There are quite a few dependencies, all listed in requirements.txt file. So, once you have python v3, just run the following command :

`pip install -r requirements.txt`

Once they're all installed, you can use the bot! 

Dockerized version coming soon. :-)

# How to use?

Thanks to [click](https://dbader.org/blog/python-commandline-tools-with-click#intro), you can actually get to know this without even reading this section. 

Just run `python app_cli.py --help`

It should present with you a guide : 

```bash
Usage: app_cli.py [OPTIONS] COMMAND [ARGS]...  

  This is a JIRA Bot written by Bhavul which is supposed to help devs in
  various ways. Check the commands listed below to know what all actions the
  bot can perform.  

Options:
  --help  Show this message and exit.  

Commands:
  jira_scraper_commentor  The commands here are used to scrape...
  mailer                  The commands here are used to send different...
  related_ticket_finder   The commands here can be used to train a...
```

There are 3 modules as you can see above: 
1. **jira_scraper_commentor** : This module can be used to scrape data from JIRA and comment on tickets. Currently, it offers a templated comment which could be commented on every ticket satisfying a JQL filter.  
  At Endurance, this was being used to comment a set of questions on every new ticket which the developer needs to answer before they close the ticket (What is the issue, How did they solve it, Can it occur again, etc.)  
2. **mailer** : This module is used for sending mails. Every mail can have its own html. Jinja2 templating engine is used.  
At Endurance this was being used to send the mail of shame - a mail which reminds developer that they have closed certain ticket but not followed the process in place.
3. **related_ticket_finder** : This module is used to train a model for tickets and then to comment related tickets on every new ticket that comes up. The idea is if you've had similar ticket in the past, the proceedings and comments of that ticket could help a developer understand ways to debug the new ticket.  
At Endurance, this was used by Wholesale team to reduce SLAs and give a head-start into how to debug a particular ticket for any developer.

Each of these modules have their own sub-commands.

For example, 
```
$ python app_cli.py related_ticket_finder --help  
 
 Usage: app_cli.py related_ticket_finder [OPTIONS] COMMAND [ARGS]...
 
   The commands here can be used to train a TF-IDF model and/or use the model
   to comment related tickets for filters defined.
 
 Options:
   --help  Show this message and exit.
 
 Commands:
   comment_related_tickets      This runs a script to comment related
                                tickets...
   get_data                     This command returns data that is being used...
   train_related_tickets_model  This runs a script to train model on all...
```

So, there are 3 commands available under `related_ticket_finder` module. You can recursively check what they do as well and what arguments they take :
 
 ```bash
 $ python app_cli.py related_ticket_finder comment_related_tickets --help  
 
   
 Usage: app_cli.py related_ticket_finder comment_related_tickets
            [OPTIONS]
 
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

For example, if I had experimented to build a new model called *'MojoJojoModel'*, and I wanted to only use that model to comment only on two JIRAs - ABC-1234, and ABC-2345. Then I could run the bot like this : 

**`python app_cli.py related_ticket_finder comment_related_tickets --test-model "/Users/bhavul.g/JiraSimilarityHelper/models/MojoJojo" --open-tickets-filter "project = ABC AND key in (ABC-1234, ABC-2345)"`**

Of course, since `--test-model` and `--open-tickets-filter` are each an **option**, so if you don't give them, it would still run. It would pick up the models defined in file **current_model_for_related_tickets.py**, and pick up the filters from **jira_filters_to_scrape.py** file. 


Further, detailed documentation for each module is available within their directories.

```bash
/jira_scraper : Readme.md contains the documentation for jira_scraper module  
  
/mailer : Readme.md contains the documentation for jira_scraper module 
  
/related_ticket_finder : Readme.md contains the documentation for related_ticket_finder module
```


# Can I have this feature?

Let's talk about it. If you can develop yourself, then go ahead, fork the repo and do it. If you think it would help all, then kindly raise a PR, and I'd love to merge it. There's also a list of upcoming features that I already have in mind which I've listed below. You could possibly help in these too.

### Upcoming features
This is a small list of features that should be coming up on this repository soon and they're already planned. They're listed in terms of their priority. 

- Finish the documentation of individual module
- A mail which could be used to send statistics of jira issues under an epic. [Tech debt reminder]
- Dockerization of this repository for easy installation, deployment and execution
- mail about data of the month for tickets
- Sort by date while printing related tickets
- Make auto-training of new models with updated tickets possible
- Use configparser for all config(settings) files instead of them being python files. 
- words-to-ignore --- if file exists only then use it. else take all.
- make cronjob a better feature and then document about cronjob.
- Addition of UI to make setting up configurations easier and showcase statistics
- Make the whole code PEP-8 standardised for 
- Add unit tests

Other than these, some minor `todo` exists in the code itself (See `jira_worker.py`, `util.py`, `mailer_helper.py` for example.). These need to be picked up as well.


# Author

Bhavul Gauri