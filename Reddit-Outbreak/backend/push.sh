# This script is meant to publish db.json to a git repository
# such that it is accessible via github pages.

cd xxx # path to where db.json is stored
git checkout gh-pages
git pull
git add .
git commit -m "updated db.json"
git push