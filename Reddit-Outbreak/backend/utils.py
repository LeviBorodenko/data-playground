from collections import namedtuple
from constants import VERBOSE


def log(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)


MonitoredSubmission = namedtuple("MonitoredSubmission",
                                 ["post_id", "db_folder", "reddit_api"])

Context = namedtuple("Context", ["db_folder", "reddit_api"])
