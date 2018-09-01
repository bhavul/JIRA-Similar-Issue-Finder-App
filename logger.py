import logging
import logzero
from raven import Client
from common_util import project_dir_path

logzero.loglevel(logging.INFO)
formatter = logzero.LogFormatter(fmt='%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s',datefmt='%d-%m-%Y %H:%M:%S')
logzero.formatter(formatter=formatter)
logzero.logfile(project_dir_path+"/logs/rotating-logfile.log", maxBytes=1e6, backupCount=3)
sentry_client = Client('https://fcb663a19b75454abc1ec43325c3687e:e25bc79f5e0943048861973e9e68ff49@sentry.io/215043')
logger = logzero.logger