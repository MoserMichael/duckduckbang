#!/bin/bash

set -ex

cd / 

python3  build_cats.py -t
python3  build_cats.py -r

stat /all_cats.html 

if [[ -z $GITHUB_TOKEN ]]; then
    echo "token does not exist, can't upload"
    exit 1
fi

git clone https://github.com/MoserMichael/duckduckbang.git duck
pushd duck
git checkout gh-pages

#cp ../all_cats.html html/all_cats.html
#if [[ $(git diff) != "" ]]; then

diff -U 0 ../all_cats.html html/all_cats.html | grep -v "Generated on" || true

CHANGED=$(diff -U 0 ../all_cats.html html/all_cats.html | grep -v "Generated on"  | wc -l)

git config --global user.email "a@gmail.com"
git config --global user.name "MoserMichael"

#tmp
CHANGED=1

if [[ $CHANGED != "3" ]]; then\
    cp -v ../*.html html/

    echo "*** pushing changed file ***"
 
    git add -v html/*.html
    git commit -m "automatic build $(date)"
    expect -f /ex
else
    echo "*** the file didn't change ***"
fi

# generate some action in the main repository, so that the CI job will not get disabled.
git checkout master
date >> ci-runs.txt
git add ci-runs.txt
git commit -m "automatic build $(date)"
expect -f /ex

popd

