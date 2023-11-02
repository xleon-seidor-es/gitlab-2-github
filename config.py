import os

class Secrets:
    gitlab_token = os.environ.get('GITLAB_TOKEN')
    gitlab_api_url = os.environ.get('GITLAB_API_URL')
    gitlab_root_group_id = os.environ.get('GITLAB_ROOT_GROUP_ID')
    gitlab_user_id = os.environ.get('GITLAB_USER_ID')
    github_api_url = os.environ.get('GITHUB_API_URL')
    github_token = os.environ.get('GITHUB_TOKEN')
    github_user = os.environ.get('GITHUB_USER')
    github_user_password = os.environ.get('GITHUB_PASSWORD')
    github_organization = os.environ.get('GITHUB_ORGANIZATION')
