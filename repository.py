import subprocess
import logging
import hashlib

class repository:
    def __init__(self, id, name, description, url, url_clone, group='', default_branch='', archived=False, wiki_exists='', wiki_url='') -> None:
        self.ID = id
        self.NAME = name
        self.DESCRIPTION = description
        self.URL = url
        self.URL_CLONE = url_clone
        self.GROUP = group
        self.DEFAULT_BRANCH = default_branch
        self.ARCHIVED = archived
        if wiki_url == '':
            self.WIKI_URL = self.URL_CLONE.replace(".git", ".wiki.git")
        else:
            self.WIKI_URL = wiki_url
        self.WIKI_EXISTS = wiki_exists

    def check_contains_wiki(self):
        has_wiki = False
        repo_hash = hashlib.sha1(self.NAME.encode()).hexdigest()[:8]
        directory = f"{self.NAME}_{repo_hash}.wiki"
        logging.debug(f"Cloning repository {self.WIKI_URL} to {directory}")
        cmd_status = subprocess.run(['git', 'clone', self.WIKI_URL, directory], capture_output=True)
        if cmd_status.returncode == 0:
            logging.debug(f"Wiki exists for repository {self.NAME}")
            self.has_wiki = True
            logging.debug(f"Removing temporary directory {directory}")
            subprocess.run(['rm', '-rf', directory])
        else:
            logging.debug(f"Wiki does not exist for repository {self.NAME}")
            self.has_wiki = False
        logging.debug(F"{cmd_status.returncode} : {cmd_status.stdout.decode('utf-8')} {cmd_status.stderr.decode('utf-8')}")
        return has_wiki

    def serialize(self):
        return {
            'id': self.ID,
            'name': self.NAME,
            'description': self.DESCRIPTION,
            'url': self.URL,
            'url_clone': self.URL_CLONE,
            'group': self.GROUP,
            'default_branch': self.DEFAULT_BRANCH,
            'archived': self.ARCHIVED,
            'wiki_exists': self.WIKI_EXISTS,
            'wiki_url': self.WIKI_URL
        }

class snippet:
    def __init__(self, id, title='', filename='', description='', ssh_url='') -> None:
        self.ID = id
        self.TITLE = title
        self.FILENAME = filename
        self.DESCRIPTION = description
        self.SSH_URL = ssh_url

    def convert_to_github_wiki(self, github_repository_url):
        TITLE = self.TITLE
        FILENAME = self.TITLE
        DESCRIPTION = self.DESCRIPTION
        SSH_URL = f"{github_repository_url.replace('.git', '.wiki.git')}"
        return snippet(self.ID, TITLE, FILENAME, DESCRIPTION, SSH_URL)
    
    def serialize(self):
        return {
            'id': self.ID,
            'title': self.TITLE,
            'filename': self.FILENAME,
            'description': self.DESCRIPTION,
            'ssh_url': self.SSH_URL
        }
