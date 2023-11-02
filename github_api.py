# Github API functions
import requests
import json
import logging
import repository

class GithubAPIClient:
    """
    A client for interacting with the GitHub API.
    Args:
        api_url (str): The base URL for the GitHub API.
        token (str): A personal access token for authenticating with the GitHub API.
        organization (str): The name of the GitHub organization to interact with.
    Attributes:
        token (str): A personal access token for authenticating with the GitHub API.
        api_url (str): The base URL for the GitHub API.
        organization (str): The name of the GitHub organization to interact with.
        headers_cli (dict): A dictionary of headers to include with API requests.
    """
    def __init__(self, api_url, token, organization) -> None:
        self.token = token
        self.api_url = api_url
        self.organization = organization
        self.headers_cli = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }

    def build_repository_from_response(self, response_json):
        logging.debug(
            f"Content to create repo: {response_json['id']}, {response_json['name']}, {response_json['description']}, {response_json['url']}, {response_json['clone_url']}, {response_json['owner']['login']}, {response_json    ['default_branch']}, {response_json['archived']}")
        repo = repository.repository(response_json['id'], response_json['name'], response_json['description'], response_json['url'],response_json['clone_url'], response_json['owner']['login'], response_json    ['default_branch'], response_json['archived'])
        logging.debug(f"Object repository created {repo.serialize()}")
        return repo

    def archive_repository(self, repo_name, archived='true'):
        logging.info(f"Archiving: {archived} repository {repo_name} in GitHub")
        url = f"{self.api_url}/repos/{self.organization}/{repo_name}"
        payload = json.dumps({
            "archived": f"{archived}"
        })
        response = requests.patch(url, headers=self.headers_cli, data=payload)
        logging.debug(response.text)
        if 'message' in response.json():
            logging.error(f"Error archiving repository {repo_name}: {response.json()['errors'][0]['message']}")
        else:
            logging.info(f"Archived repository {repo_name}")

    def create_repository(self,repo_name, description, group_id, archived=False):
        logging.info(f"Creating repository {repo_name} in GitHub")
        url = f"{self.api_url}/orgs/{self.organization}/repos"
        payload = json.dumps({
            "name": repo_name,
            "description": f"{description}",
            "private": True,
            "has_issues": True,
            "has_projects": False,
            "has_wiki": True,
            "team_id": group_id,
            "auto_init": False,
            "delete_branch_on_merge": True,
            "archived": f"{archived}"
        })
        response = requests.post(url, headers=self.headers_cli, data=payload)
        repo = None
        logging.debug(response.text)
        if 'message' in response.json():
            logging.error(f"Error creating repository {repo_name}: {response.json()['errors'][0]['message']}")
        else:
            repo = self.build_repository_from_response(response.json())
        return repo

    def get_repository(self, repo_name):
        logging.info(f"Getting repository {repo_name} from GitHub")
        url = f"{self.api_url}/repos/{self.organization}/{repo_name}"
        response = requests.get(url, headers=self.headers_cli)
        repo = None
        logging.debug(response.text)
        if 'message' in response.json():
            logging.error(f"Error creating repository {repo_name}: {response.json()['errors'][0]['message']}")
        else:        
            repo = self.build_repository_from_response(response.json())
        logging.debug(f"Repository {repo.serialize()}")
        return repo

    def rename_branch(self, repo_name, branch_name, new_branch_name):
        logging.info(f"Renaming branch {branch_name} to {new_branch_name} in repository {repo_name}")
        url = f"{self.api_url}/repos/{self.organization}/{repo_name}/branches/{branch_name}/rename"
        payload = json.dumps({
            "new_name": new_branch_name
        })
        response = requests.post(url, headers=self.headers_cli, data=payload)
        logging.debug(response.text)

    def get_group_id(self, group_name):
        logging.info(f"Getting group {group_name} from GitHub")
        url = f"{self.api_url}/orgs/{self.organization}/teams"
        response = requests.get(url, headers=self.headers_cli)
        teams = response.json()
        group_id = None
        for team in teams:
            if team['name'] == group_name:
                logging.info(f"Found group {group_name} with id {team['id']}")
                group_id = team['id']
        return group_id

    def delete_repository(self, repo_name):
        logging.info(f"Deleting repository {repo_name} from GitHub")
        url = f"{self.api_url}/repos/{self.organization}/{repo_name}"
        response = requests.delete(url, headers=self.headers_cli)
        logging.info(response.text)

    def set_repo_to_team(self, repo_name, team, permission):
        logging.info(f"Setting repository {repo_name} to team {team} with permission {permission}")
        url = f"{self.api_url}/orgs/{self.organization}/teams/{team}/repos/{self.organization}/{repo_name}"
        payload = json.dumps({
            "permission": f"{permission}"
        })
        requests.put(url, headers=self.headers_cli, data=payload)