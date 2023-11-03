#!/bin/bash

gitlab_token=${GITLAB_TOKEN}
github_token=${GITHUB_TOKEN}

sed -i "s/GITLAB_TOKEN/$gitlab_token/" settings.template
sed -i "s/GITHUB_TOKEN/$github_token/" settings.template

while read line
do
    cp settings.template settings.ts
    project_id=$(echo $line|cut -d ':' -f1)
    project_name=$(echo $line|cut -d ':' -f2)
    sed "s/PROJECT_ID/$project_id/" -i settings.ts
    sed "s/PROJECT_NAME/$project_name/" -i settings.ts
    npm run start
done < $PROJECT_LIST_FILE