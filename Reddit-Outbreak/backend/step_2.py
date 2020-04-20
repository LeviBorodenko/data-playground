from pathlib import Path
from setup import SetUp
from utils import log

from tinydb import TinyDB, Query
from tinydb.operations import set
from pandas import to_datetime

from collections import Counter
from datetime import date, timedelta
from time import sleep

from constants import COMMENT_LIMIT, MAX_COMMENT_AGE, SCAN_COOLDOWN


class RedditorScanner(object):
    """Scans the comment history of the new redditors."""

    today = to_datetime(date.today())

    def __init__(self, context):
        super(RedditorScanner, self).__init__()

        # setup link to databases
        self.db_folder = Path(context.db_folder)
        self.subreddit_db = TinyDB(self.db_folder / "subreddit.json")
        self.redditor_db = TinyDB(self.db_folder / "redditor.json")

        # setup reddit api interface
        self.reddit = context.reddit_api

    def to_scan(self):
        """Returns an iterator over not yet scanned redditors and when
        they commented.

        """
        Redditor = Query()

        result = self.redditor_db.search(Redditor.scanned == False)

        for redditor in result:

            yield self.reddit.redditor(name=redditor["name"])

    def write_down(self, redditor, history):
        """ticks the redditor as scanned in the db and adds its history.

        """
        Redditor = Query()
        self.redditor_db.update(set("scanned", True),
                                Redditor.name == redditor.name)

        self.redditor_db.update(set("history", history),
                                Redditor.name == redditor.name)

    def get_post_activity(self, redditor):

        counter = Counter()
        for comment in redditor.comments.new(limit=COMMENT_LIMIT):

            commented_at = to_datetime(comment.created_utc, unit="s")
            comment_age = (self.today - commented_at).days

            if 0 < comment_age < MAX_COMMENT_AGE:

                comment_sub_id = comment.subreddit_id
                counter[comment_sub_id] += 1

        # turn counter to dict
        counter = dict(counter)

        log(f"{redditor} commented in: {counter}")

        return {"redditor": redditor, "history": counter}

    def scan(self):

        # get datebases
        self.comment_db = TinyDB(self.db_folder / "comment.json")
        self.redditor_db = TinyDB(self.db_folder / "redditor.json")

        for redditor in self.to_scan():

            try:
                result = self.get_post_activity(redditor)
                self.write_down(**result)
            except Exception as e:
                log(f"Scanning failed, ignoring redditor {redditor}")
                self.write_down(redditor=redditor, history={})

    def start_scanning(self):

        log("Begin scanning new redditors")
        while True:

            log("Scanning new redditors")
            try:
                self.scan()
            except Exception as e:
                log(e)

            sleep(SCAN_COOLDOWN)


if __name__ == '__main__':
    setup = SetUp()
    setup.load_db()
    scanner = RedditorScanner(setup.context)

    scanner.start_scanning()
