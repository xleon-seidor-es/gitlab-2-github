# FILEPATH: ./main.py

**SUMMARY:**

This application helps to migrate repoinformation from Gitlab to Github.

**USAGE:**

```bash
python3 main.py --migrate-repo=repo_name
python3 main.py --migrate-wiki=repo_name
python3 main.py --migrate-snippets=repo_name
``````

**Features:**

```bash
Migrate all repositories from a group ans subgroups on Gitlab to Github.
Migrate all wikis.
Migrate all snippets. The snippets will added as Github Wiki.
```

**Functions:**

```bash
--migrate-repo -> Migrate repositories. Argument should be repo name or the key world "all" to migrate all repositories
--migrate-since-repo -> Migrate repositories from a specific repository to the end of the list. Argument should be repo name
--migrate-wiki -> Migrate wiki from Gitlab to Github for a single repository
--migrate-snippets -> Migrate Snippets project from Gitlab to Github for a single repository.Argument should be repo name or the key world "all" to migrate all repositories
--delete-repo -> Delete a repository. Argument should be repo name or the key world "all" to migrate all repositories
--delete-wiki -> Delete Wikis repository. Argument should be repo name or the key world "all" to migrate all repositories
--archived -> Migrate Archived repositories, this flas only migrate the archived repositories, by default is False
--archive-repos -> Archive repositories in Github, this flag only archive the repositories in Github, by default is False
--unarchive-repos -> Archive repositories in Github, this flag only archive the repositories in Github, by default is False
--list-archived-repos -> List all Gitlab archived repositories
--list-wikis -> List wiki from Gitlab 
```

**Requirements:**

```bash
Is necessary to have installed python3, git, and the following python libraries:
- selenium
```

**Before** execute the script, you need to set the following environment variables:

```bash
 - GITLAB_TOKEN=''
 - GITLAB_API_URL=""
 - GITLAB_ROOT_GROUP_ID=1234567
 - GITLAB_USER_ID=0
 - GITHUB_API_URL=""
 - GITHUB_TOKEN=''
 - GITHUB_USER=""
 - GITHUB_PASSWORD=""
 - GITHUB_ORGANIZATION=""
````

You need to load these variables before execute the script, you can do it in the following way:

```bash
. ./vars.env
```

You need to define GITLAB_ROOT_GROUP_ID to migrate a Gitlab group, this is the root group id from Gitlab, this is the group where the script will start to migrate the repositories.
If you want to migrate a personal repository, you need to define GITLAB_USER_ID, this is the user id from Gitlab.
