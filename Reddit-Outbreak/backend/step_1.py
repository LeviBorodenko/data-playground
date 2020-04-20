from setup import SetUp
import praw
from tinydb import TinyDB, Query
from time import sleep
from pandas import to_datetime

from constants import POST_URL, MAX_FETCHES, FETCH_COOLDOWN
from constants import REPLACE_LIMIT, REPLACE_TRIES
from utils import log


class SubmissionMonitor(object):
    """Monitors a thread for new commenters.

    """

    def __init__(self, monitored_submission):
        super(SubmissionMonitor, self).__init__()

        # unpack the named tuple for post and current db folder
        self.post_id = monitored_submission.post_id
        self.db_folder = monitored_submission.db_folder
        self.reddit = monitored_submission.reddit_api

        # get datebases
        self.comment_db = TinyDB(self.db_folder / "comment.json")
        self.redditor_db = TinyDB(self.db_folder / "redditor.json")

        log("Starting to monitor submissions.")

    def fetch_redditors(self):

        log("Fetching comments.")
        # load comments (up to REPLACE_LIMIT "more comments"-presses)
        post = self.reddit.submission(self.post_id)
        comments = post.comments

        for _ in range(REPLACE_TRIES):
            try:
                comments.replace_more(limit=REPLACE_LIMIT)
            except Exception as e:
                log("Handling replace_more exception:", e)
                sleep(2)

        # get flattened list of comments
        comments = comments.list()

        count_all = 0
        count_new = 0
        for comment in comments:

            count_all += 1

            # check if we have seen this comment before
            if self.is_new_comment(comment):

                # insert comment into db
                self.comment_db.insert({"id": comment.id})

                # remains to check if it is actually a new
                # redditor
                redditor = comment.author

                if redditor is None:
                    continue
                if self.is_new_redditor(redditor):

                    count_new += 1

                    self.redditor_db.insert({
                        "name": redditor.name,
                        "commented_at": str(to_datetime(comment.created_utc,
                                                        unit="s")),
                        "scanned": False,
                        "history": None,
                        "considered": False
                    })
        log(f"{count_all} comments and {count_new} new redditors.")

    def monitor(self):

        for _ in range(MAX_FETCHES):

            try:
                self.fetch_redditors()
            except Exception as e:
                log(e)

            sleep(FETCH_COOLDOWN)

    # Helper methods
    def is_new_redditor(self, redditor: praw.models.Redditor):

        Redditor = Query()
        result = self.redditor_db.search(Redditor.name == redditor.name)

        if len(result) == 0:
            return True
        else:
            return False

    def is_new_comment(self, comment):
        # query comment db is this is a new id
        Comment = Query()

        result = self.comment_db.search(Comment.id == comment.id)

        if len(result) == 0:
            return True
        else:
            return False


if __name__ == '__main__':
    setup = SetUp()
    setup.initiate_db()

    post = SubmissionMonitor(setup.get_submission(POST_URL))

    post.monitor()
