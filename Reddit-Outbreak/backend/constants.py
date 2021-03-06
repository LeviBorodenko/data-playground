from pathlib import Path

# utils
VERBOSE = True

# monitor post
REPLACE_LIMIT = 32
REPLACE_TRIES = 100
FETCH_COOLDOWN = 25  # in seconds
MAX_FETCHES = 100

# setup
CONFIG_DIR = Path("./config")
DB_DIR = Path("./dbs/")
POST_URL = "https://www.reddit.com/r/PostToMonitor"

# scan redditors
COMMENT_LIMIT = 50
MAX_COMMENT_AGE = 5  # in days
SCAN_COOLDOWN = 30

# subreddit monitor
MIN_SUB_COUNT = 2000000

# Cooldown between a cycle (all 4 steps)
COOLDOWN = 5  # in seconds
