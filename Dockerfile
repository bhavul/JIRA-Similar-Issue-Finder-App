# Get Ubuntu 18.04
FROM ubuntu:18.04

# Install python3 and dev libraries
RUN apt-get update && apt-get install -y build-essential python3 python python3-dev libxml2-dev libxslt-dev libssl-dev zlib1g-dev libyaml-dev libffi-dev python3-pip cron git locales

# Set python 3 as default
RUN ln -s /usr/bin/python3 python

# Upgrade pip
RUN pip3 install --upgrade pip requests

# Set proper locales else the app cries later
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8

ENV LANG en_US.UTF-8

# set work directory
WORKDIR /app/jira-bot

# Install pip package requirements in a way so they get cached
ADD requirements.txt /app/jira-bot/
RUN pip3 install --trusted-host pypi.python.org -r /app/jira-bot/requirements.txt

# Download nltk stopwords
RUN python3 -m nltk.downloader stopwords

# Copy the app code
COPY  .  /app/jira-bot/

# Add cron file and apply the cron
ADD crontab-test /etc/cron.d/jira-bot-cron
RUN chmod 0644 /etc/cron.d/jira-bot-cron
RUN crontab /etc/cron.d/jira-bot-cron

# Use if you just wish to run the CLI tool whenever you run the docker image and exit afterwards
# ENTRYPOINT ["python", "app_cli.py"]

# Run the cron and don't let the container die
CMD cron && tail -f /dev/null

#### TODO : add the /data waali json files as volume or some common place, so even if new docker image has to run,
old data isn't lost