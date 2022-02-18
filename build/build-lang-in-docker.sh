#!/bin/bash

set -ex

cd / 


if [[ -z $GITHUB_TOKEN ]]; then
    echo "token does not exist, can't upload"
    exit 1
fi

git clone https://github.com/MoserMichael/duckduckbang.git duck
pushd duck

python3 build_lang.py

stat description_cache.json

DID_CHANGE=$(git diff description_cache.json)

git config --global user.email "a@gmail.com"
git config --global user.name "MoserMichael"

if [[ "$DID_CHANGE" != "" ]]; then

    echo "*** pushing changed file ***"
 
    git add description_cache.json
    git commit -m "automatic build - identify language of description with fasttext $(date)"
    expect -f /ex
else
    echo "*** the file didn't change ***"
fi

# generate some action in the main repository, so that the CI job will not get disabled.
git checkout master
date >> ci-runs.txt
git add ci-runs.txt
git commit -m "automatic build - add language tag $(date)"
expect -f /ex

popd

