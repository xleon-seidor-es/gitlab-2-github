import argparse
from config import Secrets as MySecrets
from gitlab_api import GitlabAPIClient
from github_api import GithubAPIClient
import git_operator
import logging
import os
from repository import repository
from repository import snippet
import sys
import shutil
import time
import subprocess
from selenium_actions import github_initialize_wiki
import errors_handler

gitlab_client = GitlabAPIClient(MySecrets.gitlab_api_url, MySecrets.gitlab_token, MySecrets.gitlab_root_group_id)
github_client = GithubAPIClient(MySecrets.github_api_url, MySecrets.github_token, MySecrets.github_organization)

def get_projects_wiki(list_projects):
    for repo in list_projects:
        if repo.WIKI_URL != "":
            logging.info(
                f"Getting wiki from repository {repo.NAME}: {repo.WIKI_URL}")
            print(f"Wiki from repository {repo.NAME}: {repo.WIKI_URL}")

def print_projects_list(list_projects):
    for repo in list_projects:
        print(f"{repo.ID}:{repo.NAME}")
        logging.info(f"Archived repo: {repo.ID}:{repo.NAME}")

def get_projects(list_projects, archived=False):
    list_subgroups = []
    if MySecrets.gitlab_root_group_id != 0:
        gitlab_client.get_subgroups(list_subgroups, MySecrets.gitlab_root_group_id)
        logging.info(f"These are the full group list {list_subgroups}")
        for subgroup in list_subgroups:
            gitlab_client.get_projects_from_group(list_projects, subgroup, archived)
            logging.debug(f"The group {subgroup} have {list_projects.__len__()} projects")
    else:
        logging.info("No group specified...")
        logging.info("Getting user repository list...")
        gitlab_client.get_projects_from_user(list_projects, MySecrets.gitlab_user_id)
        logging.info(f"Projects from user {MySecrets.gitlab__user_group_id}, {list_projects}")

def set_default_teams(repo):
    logging.info(f"Setting default teams for repository {repo.NAME}")
    logging.info(f"Setting default teams for repository {repo.NAME} to seidor-spain")
    github_client.set_repo_to_team(repo.NAME, "seidor-spain", "push")
    logging.info(f"Setting default teams for repository {repo.NAME} to seidor-apa")
    github_client.set_repo_to_team(repo.NAME, "seidor-apa", "push")
    logging.info(f"Setting default teams for repository {repo.NAME} to maintainer")
    github_client.set_repo_to_team(repo.NAME, "maintainer", "maintain")
    logging.info(f"Setting default teams for repository {repo.NAME} to management")
    github_client.set_repo_to_team(repo.NAME, "management", "admin")

def clone_github_wiki(repo_name, url, dir):
    logging.debug(f"Clone wiki repository {repo_name} from Github")
    cmd_status = git_operator.clone_repo(url, dir)
    if cmd_status != 0:
        logging.error(f"Error cloning wiki from repository {repo_name} from Gitlab")
        logging.error(f"Error getting wiki url from repository {repo_name} from Gitlab")
        logging.warning(f"Initialize wiki with selenium into {repo_name} from Github")
        github_initialize_wiki(MySecrets.github_organization, repo_name)
        cmd_status = git_operator.clone_repo(url, dir)
        if cmd_status != 0:
            raise errors_handler.CloneWikiException(repo_name)

def copy_wiki_files(src, dst):
    logging.debug(f"Copying wiki files to repository from {src} to {dst}")
    shutil.copytree(src, dst, symlinks=False, ignore=shutil.ignore_patterns('.git'), dirs_exist_ok=True)

def clean_directory(dir, ignore_dirs=[]):
    list_files = os.listdir(dir)
    os.chdir(dir)
    for file in list_files:
        if file in ignore_dirs:
            continue
        if os.path.isdir(file):
            logging.debug(f"Deleting directory {file}")
            shutil.rmtree(file)
        else:
            logging.debug(f"Deleting file {file}")
            os.remove(file)
    os.chdir("../")

def migrate_wiki(repo):
    if not repo.WIKI_EXISTS:
        logging.warning(f"Repository {repo.NAME} has no wiki on Gitlab")
        return
    logging.info(f"Migrate wiki repository {repo.NAME} from Gitlab")
    # 1. Get wiki from Gitlab
    logging.debug(f"Cloning wiki from Gitlab repository {repo.NAME}")
    gitlab_wiki_url = repo.WIKI_URL
    gitlab_wiki_local_dir = f"gitlab_{repo.NAME}_wiki"
    cmd_status = git_operator.clone_repo(gitlab_wiki_url, f"{gitlab_wiki_local_dir}")
    if cmd_status != 0:
        logging.error(f"Error cloning wiki from Gitlab repository {repo.NAME}")
        return
    # 2. Clone repository in Github
    github_repo = github_client.get_repository(repo.NAME)
    github_wiki_url = github_repo.WIKI_URL
    logging.info(f"Setting wiki url for repository {github_repo.NAME} to {github_wiki_url}")
    github_wiki_local_dir = f"github_{github_repo.NAME}_wiki"
    logging.debug(f"Cloning wiki from Github repository {repo.NAME}")
    clone_github_wiki(repo.NAME, github_wiki_url, github_wiki_local_dir)
    # 3. Delete local wiki
    logging.debug(f"Deleting existing wiki {repo.NAME}")
    clean_directory(github_wiki_local_dir, ignore_dirs=['.git'])
    # 4. Copy wiki files to repository
    logging.info(f"Copying wiki files to repository {repo.NAME}")
    copy_wiki_files(gitlab_wiki_local_dir, github_wiki_local_dir)
    # 5. Commit changes
    logging.debug(f"Commiting changes to repository {repo.NAME}")
    os.chdir(github_wiki_local_dir)
    git_operator.add_files(['-A'])
    git_operator.commit_changes("Initial WIKI commit")
    # 6. Push changes
    logging.info(f"Pushing changes to repository {repo.NAME} on github")
    git_operator.push_changes()
    # 7. Delete local wiki
    logging.debug(f"Deleting local wiki {repo.NAME}")
    os.chdir("../")
    shutil.rmtree(github_wiki_local_dir)
    shutil.rmtree(gitlab_wiki_local_dir)

def migrate_all_wikis(repo_list):
    for repo in repo_list:
        migrate_wiki(repo)

def migrate_repo(repo):
    logging.info(
        f"Creating repository {repo.NAME} on team {repo.GROUP} in GitHub")
    team_id = github_client.get_group_id(repo.GROUP)
    github_repo = github_client.create_repository(
        repo.NAME, repo.DESCRIPTION, team_id, repo.ARCHIVED)
    if github_repo is None:
        logging.warning(f"WARN: Repository {repo.NAME} could not be created")
        github_repo = github_client.get_repository(repo.NAME)
    logging.debug(github_repo.serialize())
    # 3.1 Rename default branch from main to master
    if github_repo.DEFAULT_BRANCH != repo.DEFAULT_BRANCH:
        logging.info(
            f"Renaming default branch from {github_repo.DEFAULT_BRANCH} to {repo.DEFAULT_BRANCH}")
        github_client.rename_branch(
            repo.NAME, github_repo.DEFAULT_BRANCH, repo.DEFAULT_BRANCH)
    # 3.2 Set default teams for repository
    set_default_teams(repo)
    # 4. Configurar el mirroring desde GitLab a GitHub
    logging.info(f"Checking if mirroring to github exists on {repo.NAME}")
    mirroring_list = gitlab_client.get_mirroring_for_repository(repo.ID)
    mirror_exists = False
    for mirror in mirroring_list:
        if f"github.com/{MySecrets.github_organization}" in mirror['url']:
            logging.info(f"Mirror already exists for repository {repo.NAME}")
            mirror_exists = True
            break
    if not mirror_exists:
        logging.info(f"Creating Mirroring from Gitlab to Github for repository {repo.NAME}")
        mirror_id = gitlab_client.create_project_mirror_to_github(
            repo.ID, MySecrets.github_user, MySecrets.github_token, MySecrets.github_organization, repo.NAME)
        logging.info(f"Created mirror ID: {mirror_id} on repository {repo.NAME}")
    # 5. Clone repositories from GitLab to local
    logging.info(f"Cloning repository {repo.NAME} from GitLab")
    git_operator.clone_repo(repo.URL_CLONE, f"{repo.NAME}")
    # 6. Go to local repository
    os.chdir(repo.NAME)
    # 6.1 Set new location to push
    logging.info(f"Setting new location to push for repository {repo.NAME}")
    git_operator.set_push_location('origin', github_repo.URL_CLONE)
    # 6.2 Add files to repository
    logging.info(f"Adding files to repository {repo.NAME}")
    git_operator.branch_mofify(github_repo.DEFAULT_BRANCH)
    # 6.3 Push changes
    try:
        logging.info(f"Pushing changes to repository {repo.NAME}")
        git_operator.push_changes_branch('origin', github_repo.DEFAULT_BRANCH)
    except Exception as error:
        logging.error(f"Pushing changes to repository {repo.NAME}: {str(error)}")
        logging.warning(f"Execute LFS fix proccess for {repo.NAME}: {str(error)}")
        git_operator.fix_lfs_errors()
    # 7. Delete local repository
    logging.info(f"Deleting local repository {repo.NAME}")
    os.chdir("../")
    shutil.rmtree(repo.NAME)

def migrate_all_repos(repo_list, initial_index=0):
    for repo in repo_list[initial_index:]:
        time.sleep(1)
        logging.info(f"Processing repository {repo.NAME}")
        migrate_repo(repo)

def rename_snippets_files_to_textfile(directoy):
    logging.info(f"Renaming snippets files to textfile on directory {directoy}")
    for root, dirs, files in os.walk(directoy):
        for file in files:
            logging.debug(f"Renaming file: {file}")
            file_path = os.path.join(root, file)
            file_name, extension = os.path.splitext(file)
            if extension in (".md", ".textfile"):
                return
            new_name = f"{file_name}.textfile"
            new_path = os.path.join(root, new_name)
            shutil.move(file_path, new_path)
            logging.debug(f"File moved: {file_path} -> {new_path}")

def migrate_snippet(repo):
    logging.info(f"Migrate snippets from Gitlab repository {repo.NAME}")
    snippets_list = []
    gitlab_client.get_snippets_list(snippets_list, repo.ID)
    logging.debug(f"Snippets list has {snippets_list.__len__()} snippets")
    if snippets_list.__len__() == 0:
        logging.info(f"Repository {repo.NAME} has no snippets")
        return
    # 1. Get repository from Github
    logging.debug(f"Get Github repository {repo.NAME}")
    github_repo = github_client.get_repository(repo.NAME)
    github_wiki_url = f"{github_repo.URL_CLONE}".replace(".git", ".wiki.git")
    logging.info(f"Setting wiki url for repository {github_repo.NAME} to {github_wiki_url}")
    github_wiki_local_dir = f"github_{github_repo.NAME}_wiki"
    logging.debug(f"Cloning wiki from Github repository {repo.NAME}")
    clone_github_wiki(repo.NAME, github_wiki_url, github_wiki_local_dir)
    for snippet in snippets_list:
        logging.info(f"Creating snippet {snippet.TITLE} on repository {repo.NAME}")
        gitlab_snippet_dir = f"gitlab_{snippet.TITLE.replace(' ', '_')}"
        gitlab_snippet_dir = gitlab_snippet_dir.replace('/', '')
        gitlab_snippet_dir = gitlab_snippet_dir.replace('__', '_')
        github_snippet_dir = f"{github_wiki_local_dir}/{gitlab_snippet_dir.replace('gitlab_', '')}"
        logging.debug(f"Clone Gitlab Snippet on local directory: {gitlab_snippet_dir}")
        cmd_status = git_operator.clone_repo(snippet.SSH_URL, f"{gitlab_snippet_dir}")
        if cmd_status != 0:
            logging.error(f"Error cloning Snippet: {snippet.SSH_URL} from Gitlab repository {repo.NAME}")
            return
        # 3. Copy snippet files to wiki repository
        logging.debug(f"Create Snippet directory: {github_snippet_dir}")
        try:
            os.mkdir(github_snippet_dir)
        except FileExistsError:
            logging.debug(f"Snippet directory already exists: {github_snippet_dir}")
        logging.info(f"Copying wiki files to repository {snippet.TITLE}")
        copy_wiki_files(gitlab_snippet_dir, github_snippet_dir)
        rename_snippets_files_to_textfile(github_snippet_dir)
        # 4. Commit changes
        logging.debug(f"Commiting changes to wiki {snippet.TITLE}")
        os.chdir(github_wiki_local_dir)
        git_operator.add_files(['-A'])
        git_operator.commit_changes("Add snippet: " + snippet.TITLE)
        os.chdir('../')
        # 6. Delete local snippet
        logging.debug(f"Deleting local snippet directory {gitlab_snippet_dir}")
        shutil.rmtree(gitlab_snippet_dir)
    # 5. Push changes
    os.chdir(github_wiki_local_dir)
    logging.info(f"Pushing changes to repository {snippet.TITLE} on github")
    git_operator.push_changes()
    os.chdir('../')
    # 7. Delete local wiki
    logging.debug(f"Deleting local wiki {repo.NAME}")
    #shutil.rmtree(github_wiki_local_dir)

def migrate_all_snippets(repo_list):
    for repo in repo_list:
        migrate_snippet(repo)

def search_repo_by_name(repo_name, repo_list):
    logging.info(f"looking for repo: {repo_name}")
    repository = None
    for repo in repo_list:
        if repo_name == repo.NAME:
            logging.info(f"Found repo: {repo_name}")
            repository = repo
    logging.warning(f"Repo {repo_name} not found")
    return repository

def delete_github_repo(repo):
    logging.info(
        f"Deletting repository {repo.NAME} from team {repo.GROUP} in GitHub")
    github_client.delete_repository(repo.NAME)
    mirroring_list = gitlab_client.get_mirroring_for_repository(repo.ID)
    for mirror in mirroring_list:
        if f"github.com/{MySecrets.github_organization}" in mirror['url']:
            logging.info(f"Deletting Github mirroring on repo: {repo.NAME}")
            gitlab_client.delete_mirror_from_repository(repo.ID, mirror['id'])
            break

def delete_all_github_wiki(repo_list):
    logging.info("Delete all wiki from Github repository")
    for repo in repo_list:
        if repo.WIKI_EXISTS:
            logging.info(f"Delete wiki for Github {repo.NAME}")
            delete_github_wiki(repo)

def delete_github_wiki(repo):
    logging.info(f"Delete wikis from Gitlab repository {repo.NAME}")
    # 1. Get repository from Github
    logging.debug(f"Get Github repository {repo.NAME}")
    github_repo = github_client.get_repository(repo.NAME)
    github_wiki_local_dir = f"github_{github_repo.NAME}_wiki"
    logging.debug(f"Cloning wiki from Github repository {repo.NAME}")
    clone_github_wiki(repo.NAME, repo.WIKI_URL, github_wiki_local_dir)
    clean_directory(github_wiki_local_dir)
    os.chdir(github_wiki_local_dir)
    git_operator.add_files(['-A'])
    git_operator.commit_changes("Delete wiki")
    git_operator.push_changes()
    # 7. Delete local wiki
    logging.debug(f"Deleting local wiki {repo.NAME}")
    os.chdir("../")
    shutil.rmtree(github_wiki_local_dir)

def main():
    logging.basicConfig(
        filename='gitlab-2-github.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    list_projects = []
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    parser = argparse.ArgumentParser(
        description='Migrate repositories from Gitlab to GitHub')
    parser.add_argument('--migrate-repo', type=str,help='Migrate repositories. Argument should be repo name or the key world "all" to migrate all repositories')
    parser.add_argument('--migrate-since-repo', type=str,help='Migrate repositories from a specific repository to the end of the list. Argument should be repo name')
    parser.add_argument('--migrate-wiki', type=str,help='Migrate wiki from Gitlab to Github for a single repository')
    parser.add_argument('--migrate-snippets', type=str,help='Migrate Snippets project from Gitlab to Github for a single repository.Argument should be repo name or the key world "all" to migrate all repositories')
    parser.add_argument('--delete-repo', type=str,help='Delete a repository. Argument should be repo name or the key world "all" to migrate all repositories')
    parser.add_argument('--delete-wiki', type=str,help='Delete Wikis repository. Argument should be repo name or the key world "all" to migrate all repositories')
    parser.add_argument('--archived', type=bool, default=False,help='Migrate Archived repositories, this flas only migrate the archived repositories, by default is False')
    parser.add_argument('--archive-repos', type=str,help='Archive repositories in Github, this flag only archive the repositories in Github, by default is False')
    parser.add_argument('--unarchive-repos', type=str,help='Archive repositories in Github, this flag only archive the repositories in Github, by default is False')
    parser.add_argument('--list-archived-repos', action='store_true',help='List all Gitlab archived repositories')
    parser.add_argument('--list-wikis', action='store_true',help='List wiki from Gitlab ')
    args = parser.parse_args()

    if args.migrate_repo is None and args.migrate_since_repo is None and args.migrate_wiki is None and args.migrate_snippets is None and args.delete_repo is None and args.delete_wiki is None and args.archive_repos is None and args.unarchive_repos is None and args.list_archived_repos is False and args.list_wikis is False:
        logging.info("No action specified, exiting...")
        sys.exit(1)
    get_projects(list_projects, args.archived)
    if args.migrate_repo and not args.migrate_wiki:
        repo_name = args.migrate_repo
        if repo_name == "all":
            migrate_all_repos(list_projects)
        else:
            repo = search_repo_by_name(repo_name, list_projects)
            migrate_repo(repo)
    elif args.migrate_since_repo and not args.migrate_wiki:
        initial_index = 0
        repo_name = args.migrate_since_repo
        repo = search_repo_by_name(repo_name, list_projects)
        initial_index = list_projects.index(repo)
        migrate_all_repos(list_projects, initial_index)
    elif args.migrate_wiki:
        if args.migrate_wiki == "all":
            migrate_all_wikis(list_projects)
        else:
            repo_name = args.migrate_wiki
            repo = search_repo_by_name(repo_name, list_projects)
            migrate_wiki(repo)
    elif args.migrate_snippets:
        if args.migrate_snippets == "all":
            migrate_all_snippets(list_projects)
        else:
            repo_name = args.migrate_snippets
            repo = search_repo_by_name(repo_name, list_projects)
            migrate_snippet(repo)
    elif args.delete_repo:
        repo_name = args.delete_repo
        repo = search_repo_by_name(repo_name, list_projects)
        delete_github_repo(repo)
    elif args.delete_wiki:
        if args.delete_wiki == "all":
            delete_all_github_wiki(list_projects)
        else:
            repo_name = args.delete_wiki
            repo = search_repo_by_name(repo_name, list_projects)
            delete_github_wiki(repo)
    elif args.archive_repos:
        repo_name = args.archive_repos
        github_client.archive_repository(repo_name, 'false')
    elif args.unarchive_repos:
        if args.unarchive_repos == "all":
            for repo in list_projects:
                repo_name = repo.NAME
                github_client.archive_repository(repo_name, 'false')
        else:
            repo_name = args.unarchive_repos
            github_client.archive_repository(repo_name, 'false')
    elif args.list_archived_repos:
        archived_projects = []
        get_projects(archived_projects, True)
        print_projects_list(archived_projects)
    elif args.list_wikis:
        get_projects_wiki(list_projects)

if __name__ == "__main__":
    main()
