from pathlib import Path
from setup import SetUp
from utils import log

from tinydb import TinyDB, Query
from tinydb.operations import set
from pandas import to_datetime, read_csv
from pandas.errors import EmptyDataError

from collections import Counter
from datetime import date, timedelta
from time import sleep, time

from constants import MIN_SUB_COUNT

from csv import DictWriter
from pathlib import Path

# fieldnames for saving to csv files
FIELDNAMES = ["S", "In", "D", "R", "T"]


class CaseCollector(object):
    """Collects the cases from the new redditors."""

    def __init__(self, context):
        super(CaseCollector, self).__init__()

        # setup path to databases
        self.db_folder = Path(context.db_folder)

        self.redditor_db_path = self.db_folder / "redditor.json"
        self.subreddit_db_path = self.db_folder / "subreddit.json"

        # setup reddit api interface
        self.reddit = context.reddit_api

    def not_considered_users(self):

        # we iterate over all non considered but scanned
        # users and return their subreddit id
        redditor_db = TinyDB(self.redditor_db_path)
        Redditor = Query()

        # we have collected its history
        cond1 = Redditor.scanned == True

        # history is not empty
        cond3 = Redditor.history != {}

        # haven't considered it before
        cond2 = Redditor.considered == False

        query = cond1 & cond2 & cond3

        result = redditor_db.search(query)

        for user in result:
            yield user

    def new_cases(self):
        """iterates over unconsidered redditors and collects
        new cases.
        """

        new_cases = Counter()

        redditor_db = TinyDB(self.redditor_db_path)
        Redditor = Query()

        for user in self.not_considered_users():
            history = user["history"]

            # convert to counter and add to all cases
            new_cases += Counter(history)

            # tick in db as considered
            redditor_db.update(set("considered", True),
                               Redditor.name == user["name"])

        return new_cases


class Pandemic(object):
    """Manages the pandemic in each subreddit"""

    def __init__(self, context):
        super(Pandemic, self).__init__()

        # setup path to databases
        self.db_folder = Path(context.db_folder)

        self.subreddit_db_path = self.db_folder / "subreddit.json"

        # setup reddit api interface
        self.reddit = context.reddit_api

    def is_new_outbreak(self, subreddit_id):
        """Check if sub is tracked or not yet tracked.
        """

        subreddit_db = TinyDB(self.subreddit_db_path)

        # first we check if the sub is in our db
        Subreddit = Query()
        query = Subreddit.id == subreddit_id

        result = subreddit_db.search(query)

        # already in db
        if len(result) != 0:
            return result[0]

        return True

    def analyse_subreddit(self, subreddit_id):

        # else we need to check if the sub is big enough
        subreddit = self.sub_id_to_sub(subreddit_id)

        name = subreddit.display_name
        subscribers = subreddit.subscribers

        if subscribers >= MIN_SUB_COUNT:
            return dict(subreddit=name,
                        S_0=subscribers,
                        id=subreddit_id,
                        too_small=False)
        else:
            return dict(subreddit=name,
                        S_0=subscribers,
                        id=subreddit_id,
                        too_small=True)

    def sub_id_to_sub(self, sub_id):
        return list(self.reddit.info([sub_id]))[0]

    def track(self, analysis, cases):

        # create pandemic database
        path = self.db_folder / "pandemic" / f"{analysis['subreddit']}.json"

        # add first entry
        time_stamp = time()
        entry = dict(E_n=cases, time_stamp=time_stamp)
        entry = dict(**entry, **analysis)

        if not entry["too_small"]:
            outbreak_db = TinyDB(path)
            outbreak_db.insert(entry)

    def track_outbreaks(self, new_cases):

        subreddit_db = TinyDB(self.subreddit_db_path)

        for sub_id in new_cases:

            # will either be the tracked subreddit's db entry
            # or true if it is untracked.
            is_new_outbreak = self.is_new_outbreak(sub_id)

            # analyse if this is a case from
            # a new subreddit
            if is_new_outbreak is True:

                # analyse new subreddit
                analysis = self.analyse_subreddit(sub_id)

                # if it is worth tracking, initiate
                # a new outbreak

                # insert into subreddit db
                subreddit_db.insert(analysis)
                self.track(analysis, cases=new_cases[sub_id])

                if not analysis["too_small"]:

                    sub_name = analysis['subreddit']
                    log(f"Started pandemic tracking in {sub_name}")

                    # create pandemic csv
                    path_dir = self.db_folder / "outbreaks"
                    path_csv = path_dir / f"{sub_name}.csv"
                    path_dir.mkdir(exist_ok=True, parents=True)
                    path_csv.touch()

            else:

                # track
                self.track(is_new_outbreak, cases=new_cases[sub_id])
                log(f"Updated pandemic in {is_new_outbreak['subreddit']}")

        # Get tracked sub_ids not in new_cases and add E_n=0
        for subreddit in subreddit_db:
            if subreddit["id"] not in new_cases.keys():

                # track with 0 cases
                self.track(subreddit, 0)

    def iter_over_outbreaks(self):
        subreddit_db = TinyDB(self.subreddit_db_path)

        for subreddit in subreddit_db:
            if not subreddit["too_small"]:

                name = subreddit["subreddit"]
                S_0 = subreddit["S_0"]

                outbreak_dir = self.db_folder / "outbreaks"
                outbreak_csv = outbreak_dir / f"{name}.csv"

                try:
                    outbreak_data = read_csv(outbreak_csv)

                    newest = outbreak_data.tail(1)
                    S = int(newest.S)
                    In = int(newest.In)
                    D = int(newest.D)
                    R = int(newest.R)

                # check if file is empty
                except EmptyDataError:
                    S = None
                    In = None
                    D = None
                    R = None

                # get the last entry in the pandemic db
                pandemic_db = TinyDB(self.db_folder / "pandemic" / f"{name}.json")

                newest = list(pandemic_db)[-1]
                E_n = newest["E_n"]
                time_stamp = newest["time_stamp"]

                yield {
                    "name": name,
                    "pandemic_dir": outbreak_dir,
                    "S_0": S_0,
                    "S": S,
                    "In": In,
                    "D": D,
                    "R": R,
                    "E_n": E_n,
                    "time_stamp": time_stamp
                }

    def spread_disease(self):

        log("Spreading the disease")
        for outbreak in self.iter_over_outbreaks():
            E_n = outbreak["E_n"]
            if E_n > 0:
                log(f"{E_n} more cases in {outbreak['name']}")

            model = SIRD(**outbreak)
            model.time_step(E_n)
            model.write_state()


class SIRD(object):
    """Simulates an SIRD outbreak


    Keyword Arguments:
        pop_size {int} -- (default: {1000})
        reproduction_number {float} --  (default: {3})
        disease_duration {int} --  (default: {14})
        death_prob {float} --  (default: {0.03})
        recovery_prob {float} --  (default: {0.8})
        healthcare_capacity {int} -- once exceeded, doubles
            the death rate (default: {None})
    """

    def __init__(
        self,
        S_0: int,
        pandemic_dir: Path,
        name: str,
        reproduction_number: float = 1,
        disease_duration: int = 80,
        death_prob: float = 0.03,
        recovery_prob: float = 0.8,
        time_delta: float = 0.02,
        S: int = None,
        In: int = None,
        D: int = None,
        R: int = None,
        time_stamp=None,
        **kwargs,
    ):
        super(SIRD, self).__init__()

        # save values
        self.S_0 = S_0
        self.R_0 = 1 + reproduction_number / disease_duration
        self.T_d = disease_duration
        self.name = name
        self.pandemic_dir = Path(pandemic_dir)
        self.time_stamp = time_stamp
        self.time_delta = time_delta

        # probability to die
        self.p_d = death_prob / disease_duration

        # probability to recover within the first "disease_duration"
        self.p_r = recovery_prob / disease_duration

        # hospital capacity, death rate climbs once we are over it
        self.h_c = int(max([S_0 / 10000, 100000]))

        # implied quantities
        self.beta = self.R_0 / S_0

        # define compartment counts if none given
        if S is None:
            self.S = S_0
            self.In = 0
            self.R = 0
            self.D = 0
        else:

            self.S = S
            self.In = In
            self.R = R
            self.D = D

    def time_step(self, E_n: int = 0):

        # Infections from outside
        # E_n = outside_infections
        dt = self.time_delta

        # Infections from infected
        new_infections = self.beta * self.S * self.In * dt + E_n

        if self.S - new_infections < 0:
            new_infections = int(self.S)

        # deaths
        new_deaths = self.p_d * self.In * dt

        if self.h_c is not None:
            if new_infections > self.h_c:
                new_deaths *= 2

        # recoveries
        new_recov = self.p_r * self.In * dt

        # update compartments
        self.S = max(self.S - new_infections, 0)
        self.In = max(self.In + new_infections - new_deaths - new_recov, 0)
        self.In = min(self.In, self.S_0)

        self.D = min(self.D + new_deaths, self.S_0)
        self.R = min(self.R + new_recov, self.S_0)

    def _state(self):
        state = dict(
            S=round(self.S, 2),
            In=round(self.In, 2),
            D=round(self.D, 2),
            R=round(self.R, 2),
            T=self.time_stamp,
        )

        return state

    @property
    def state(self):
        return self._state()

    def write_state(self):
        """Adds a line to the csv keeping track of the
        pandemic. It finds its csv file automatically by
        looking for its name.

        [description]
        """

        csv_file_path = Path(self.pandemic_dir) / f"{self.name}.csv"

        with open(csv_file_path, "a") as csv_file:
            writer = DictWriter(csv_file, FIELDNAMES)

            # check if file is empty
            if csv_file_path.stat().st_size == 0:
                writer.writeheader()

            # write state to file
            writer.writerow(self.state)


if __name__ == '__main__':
    setup = SetUp()
    setup.load_db()

    context = setup.context

    case_collector = CaseCollector(context)
    pandemic = Pandemic(context)

    new_cases = case_collector.new_cases()
