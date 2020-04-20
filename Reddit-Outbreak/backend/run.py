from setup import SetUp
from step_1 import SubmissionMonitor
from step_2 import RedditorScanner
from step_3 import CaseCollector, Pandemic
from step_4 import Analyser

from constants import POST_URL, COOLDOWN
from utils import log


from time import sleep

if __name__ == '__main__':
    setup = SetUp()
    setup.load_db()

    # initate post monitoring
    post = SubmissionMonitor(setup.get_submission(POST_URL))

    context = setup.context

    # initate redditor analyser
    scanner = RedditorScanner(context)

    # initiate case collector
    case_collector = CaseCollector(context)

    # initiate pandemic runner
    pandemic = Pandemic(context)

    # start visualising
    analyser = Analyser(context)

    counter = 0
    while True:

        # first we collect new commenter
        post.fetch_redditors()

        # then we scan the new commenters for their
        # history
        scanner.scan()

        # we then collect the new cases from the new
        # histories
        new_cases = case_collector.new_cases()

        # Initate new outpreaks
        pandemic.track_outbreaks(new_cases)

        # spread the disease
        pandemic.spread_disease()

        if counter % 20 == 0:

            analyser.create_db()
            analyser.push()

        counter += 1

        # sleep before repeating
        log("sleeping.")
        sleep(COOLDOWN)
