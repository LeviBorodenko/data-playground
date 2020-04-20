# from base_model import model
import json
import praw
import datetime
from random import randint
from pathlib import Path
from tinydb import TinyDB, Query

from utils import MonitoredSubmission, log, Context
from constants import POST_URL, CONFIG_DIR, DB_DIR


class SetUp(object):
    """Sets up the file structure and reddit api"""

    def _load_configurations(self,
                             monitor_config_file="monitor.config",
                             auth_config_file="auth.config"):

        # load monitoring settings
        with open(CONFIG_DIR / monitor_config_file) as config_file:

            configs = json.load(config_file)
            self.redditor_config = configs["redditor"]
            self.sub_config = configs["subreddit"]

        # load reddit api auth settings
        with open(CONFIG_DIR / auth_config_file) as auth_file:

            self.auth_data = json.load(auth_file)

        # time stamp of loading
        self.identifier = randint(0, 50000)

    def __init__(self):

        # configure using monitor.config
        self._load_configurations()

        # create reddit api interface
        self.reddit = praw.Reddit(**self.auth_data)

        log(f"Connected to reddit.")

    def initiate_db(self):
        """Initiates folder containing databases
        and the db.config file.
        """

        # create db folders
        db_folder = DB_DIR / f"db_{self.identifier}"
        db_folder.mkdir(exist_ok=True, parents=True)

        db_pandemic = db_folder / "pandemic"
        db_pandemic.mkdir(exist_ok=True)

        # create the databases
        self.db_subreddit = TinyDB(db_folder / "subreddit.json")
        self.db_redditor = TinyDB(db_folder / "redditor.json")
        self.db_comment = TinyDB(db_folder / "comment.json")

        # create db.config file
        db_config = {"db_folder": str(db_folder)}
        self.db_folder = db_folder

        with open(CONFIG_DIR / "db.config", "w") as db_file:
            json.dump(db_config, db_file)

        log(f"Initiated database at {db_folder}")

    def load_db(self):

        db_config_path = CONFIG_DIR / "db.config"

        if not db_config_path.exists():
            raise AssertionError("No initiated database found.")

        with open(db_config_path, "r") as db_config_file:
            db_config = json.load(db_config_file)

            self.db_folder = Path(db_config["db_folder"])

        print(f"loaded database at {self.db_folder}")

    def get_submission(self, submission_url: str):

        # get submission instance from internal reddit api
        submission = self.reddit.submission(url=submission_url)

        response = MonitoredSubmission(post_id=submission.id,
                                       db_folder=self.db_folder,
                                       reddit_api=self.reddit)

        return response

    @property
    def context(self):
        return Context(db_folder=self.db_folder,
                       reddit_api=self.reddit)


if __name__ == '__main__':
    SetUp().load_db()
