# Gitlab API connection tools
import requests
import json
import logging
import repository


class GitlabAPIClient:
    def __init__(self, api_url, token, main_group_id) -> None:
        self.token = token
        self.api_url = api_url
        self.main_group_id = main_group_id
        self.headers_request = {"PRIVATE-TOKEN": f"{self.token}",
                            'Content-Type': 'application/json'
                            }

    def get_subgroups(self, list_groups, group_id):
        logging.debug(f"getting groups from {group_id} to list")
        response = requests.get(f"{self.api_url}/groups/{group_id}/subgroups?per_page=100",  headers=self.headers_request)
        subgroups_list = response.json()
        for subgroup in subgroups_list:
            logging.debug(f"Add subgroup {subgroup['id']} to list")
            list_groups.append(subgroup['id'])
            self.get_subgroups(list_groups, subgroup['id'])
        if not subgroups_list:
            return

    def get_project_from_response(self, response_json):
        logging.debug(f"Project {response_json['id']}")
        logging.debug(f"Content to create repo: {response_json['id']}, {response_json   ['path_with_namespace'].split('/')[-1]}, {response_json['description']}, {response_json    ['web_url']}, {response_json['ssh_url_to_repo']}, {response_json['namespace']['name']},     {response_json['default_branch']}, {response_json['archived']}")
        repo_project = repository.repository(response_json['id'], response_json    ['path_with_namespace'].split('/')[-1], response_json['description'], response_json ['web_url'], response_json['ssh_url_to_repo'], response_json['namespace']['name'],   response_json['default_branch'], response_json['archived'])
        logging.debug(f"Project created {repo_project.serialize()}")
        return repo_project

    def get_project_list_from_response(self, response_json):
        list_projects = []
        for project in response_json:
            logging.debug(f"Project {project['id']}")
            repo_project = self.get_project_from_response(project)
            list_projects.append(repo_project)
        return list_projects

    # Get all projects from group
    def get_projects_from_group(self, list_projects, group_id, archived=False):
        logging.debug(f"Get projects from group {group_id}")
        response = requests.get(f"{self.api_url}/groups/{group_id}/projects?archived={archived}&per_page=100", headers=self.headers_request)
        if response.status_code == 200:
            if response.json() != []:
                list_projects.extend(self.get_project_list_from_response(response.json()))
        else:
            logging.error(f"Error getting projects from group {group_id}: {response.status_code}")

    def get_projects_from_user(self, list_projects, user_id):
        logging.debug(f"Get projects from user: {user_id}")
        response = requests.get(f"{self.api_url}/users/{user_id}/projects?per_page=100",     headers=self.headers_request)
        logging.debug(f"Projects from group {user_id}: {response.json()}")
        if response.status_code == 200:
            list_projects.extends(self.get_project_list_from_response(response.json()))
        else:
            logging.error(
                f"Error getting projects from user {user_id}: {response.status_code}")

    def get_project_by_id(self, repo_id):
        project = None
        logging.info(f"Get projects from group {repo_id}")
        response = requests.get(f"{self.api_url}/projects/{repo_id}", headers=self.headers_request)
        logging.info(f"Parse projects from group {repo_id}")
        if response.status_code == 200:
            project = self.get_project_from_response(response.json())
        else:
            logging.error(
                f"Error getting projects from group {repo_id}: {response.status_code}")
        return project

    def get_project_wiki_exist(self, repo_id):
        logging.debug(f"Getting Wikis exists from project {repo_id}")
        response = requests.get(f"{self.api_url}/projects/{repo_id}/wikis",headers=self.headers_request)
        if response.json() != []:
            logging.info(f"Project {repo_id} has Wikis: {response.json()}")
            return True
        logging.info(f"Project {repo_id} has no Wikis")
        return False

    def create_project_mirror_to_github(self, gitlab_project_id, github_user,  github_token, github_organization, repo_name):
        github_mirror = f"https://{github_user}:{github_token}@github.com/{github_organization}/{repo_name}.git"
        logging.debug({github_mirror})
        payload = {
            "url": github_mirror,
            "enabled": True
        }
        logging.info(payload)
        response = requests.post(f"{self.api_url}/projects/{gitlab_project_id}/remote_mirrors", headers=self.headers_request, json=payload, )
        logging.info(response.text)
        return response.json()['id']

    def delete_mirror_from_repository(self, repo_id, mirror_id):
        logging.info(f"Deleting mirror {mirror_id} from repository {repo_id}")
        requests.delete(
            f"{self.api_url}/projects/{repo_id}/remote_mirrors/{mirror_id}", headers=self.headers_request)

    def get_mirroring_for_repository(self, repo_id):
        logging.info(f"Getting mirrors from repository {repo_id}")
        response = requests.get(
            f"{self.api_url}/projects/{repo_id}/remote_mirrors", headers=self.headers_request)
        logging.info(response.json())
        return response.json()
    
    def get_snippets_list(self, snippet_list, repo_id):
        logging.info(f"Getting snippets from repository {repo_id}")
        response = requests.get(f"{self.api_url}/projects/{repo_id}/snippets", headers=self.headers_request)
        logging.debug(response.json())
        for field in response.json():
            logging.debug(f"Getting snippet {field['id']}: {field['title']}")
            snippet = repository.snippet(field['id'], field['title'], field['file_name'], field['description'], field['ssh_url_to_repo'])
            logging.debug(f"Adding snippet {snippet.serialize()} to list")
            snippet_list.append(snippet)
        logging.debug(f"Snippets list: {snippet_list}")