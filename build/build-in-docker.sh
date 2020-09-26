#!/bin/bash

set -ex

cd / 

python3  /build-cats.py

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


CHANGED=$(diff -U 0 ../all_cats.html html/all_cats.html | grep -v "Generated on"  | wc -l)

if [[ $CHANGED != "3" ]]; then
    cp ../all_cats.html html/all_cats.html

    echo "*** pushing changed file ***"
 
    git config --global user.email "a@gmail.com"
    git config --global user.name "MoserMichael"

    git add html/all_cats.html
    git commit -m "automatic build $(date)"
    expect -f /ex
else
    echo "*** the file didn't change ***"
fi

popd

