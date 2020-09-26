#!/bin/bash

set -ex

cd / 

python3  /build-cats.py

stat /all_cats.html 

git clone https://github.com/MoserMichael/duckduckbang.git duck
pushd duck
git checkout gh-pages
git branch
ls -al

cp ../all_cats.html html/all_cats.html
if [[ $(git diff) != "" ]]; then
    echo "*** pushing changed file ***"
 
    git config --global user.email "a@gmail.com"
    git config --global user.name "MoserMichael"

    if [[ -z $GITHUB_TOKEN ]]; then
        echo "token does not exist, can't upload"
        exit 0
    fi
    git add html/all_cats.html
    git commit -m "automatic build $(date)"
    expect -f /ex
else
    echo "*** the file didn't change ***"
fi
popd

