class CloneWikiException(Exception):
    def __init__(self, repo_name):
        self.repo_name = repo_name
        super().__init__(
            f"Error cloning wiki from repository {repo_name} from Gitlab")
