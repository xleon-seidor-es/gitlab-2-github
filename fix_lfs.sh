#!/bin/bash
set -e

url_repo=$1
repodir=$(echo $url_repo | sed 's/.*\///' | sed 's/.git//')
since_branch=$(sed 's| |/r/n|g'|grep 'since_branch='|cut -d '=' -f2)

git clone $url_repo
git remote set-url --push origin https://github.com/seidor-cx/${repodir}.git

list_branches=$(git branch -r | grep -v HEAD | sed 's/origin\///')

if [ -n "$since_branch" ]; then
    list_branches=$(echo $list_branches | sed "s/$since_branch//g")
fi

for branch in $list_branches
do
    echo "Fixing LFS for branch $branch"
    git checkout $branch
    git lfs install
    git lfs migrate import --above=50Mb --include-ref=$branch
    git push -f origin $branch
done