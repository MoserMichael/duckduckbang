#!/bin/bash

set -ex

cd / 


if [[ -z $GITHUB_TOKEN ]]; then
    echo "token does not exist, can't upload"
    exit 1
fi

python3 build_lang.py


git clone https://github.com/MoserMichael/duckduckbang.git duck
pushd duck

cp ../description_cache.json .

git status

DID_CHANGE=$(git diff description_cache.json)

git config --global user.email "a@gmail.com"
git config --global user.name "MoserMichael"

if [[ "$DID_CHANGE" == "" ]]; then
    echo "*** the file didn't change ***"
    exit 1
fi


echo "*** pushing changed file ***"

git add description_cache.json
git commit -m "automatic build - identify language of description with fasttext $(date)"
expect -f /ex

popd

