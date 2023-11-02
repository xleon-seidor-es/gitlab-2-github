import subprocess
import os
import logging

def init_repo(directory):
    logging.debug(f"Initializing repository in {directory}")
    os.chdir(directory)
    cmd_status = subprocess.run(['git', 'init'], capture_output=True)
    return cmd_status.returncode

def add_files(files):
    logging.debug(f"Adding files: {files} to repository")
    cmd_status = subprocess.run(['git', 'add'] + files, capture_output=True)
    return cmd_status.returncode

def commit_changes(message):
    logging.debug("Commiting changes to repository")
    cmd_status = subprocess.run(['git', 'commit', '-m', message], capture_output=True)
    return cmd_status.returncode

def push_changes(remote='origin', branch='master'):
    logging.debug(f"Pushing changes to {remote} {branch}")
    cmd_status = subprocess.run(['git', 'push', remote, branch], capture_output=True)
    return cmd_status.returncode

def pull_changes(remote='origin', branch='master'):
    logging.debug(f"Pulling changes from {remote} {branch}")
    cmd_status = subprocess.run(['git', 'pull', remote, branch], capture_output=True)
    return cmd_status.returncode

def clone_repo(url, directory):
    logging.debug(f"Cloning repository {url} to {directory}")
    cmd_status = subprocess.run(['git', 'clone', url, directory], capture_output=True)
    logging.debug(f"{cmd_status.returncode} : {cmd_status.stdout.decode('utf-8')} {cmd_status.stderr.decode('utf-8')}")
    return cmd_status.returncode

def clone_repo_mirror(url, directory):
    logging.debug(f"Cloning mirror repository {url} to {directory}")
    cmd_status = subprocess.run(['git', 'clone', '--mirror', url, directory], capture_output=True)
    return cmd_status.returncode

def set_push_location(remote='origin', new_location='master' ):
    logging.debug(f"Setting push location to {new_location}")
    cmd_status = subprocess.run(['git', 'remote', 'set-url', '--push', remote, new_location], capture_output=True)
    return cmd_status.returncode

def push_mirror():
    logging.debug("Fetching mirror")
    subprocess.run(['git', 'fetch', '-p'])
    logging.debug("Pushing mirror")
    cmd_status = subprocess.run(['git', 'push', '--mirror'], capture_output=True)
    return cmd_status.returncode

def add_remote(remote, url):
    logging.debug(f"Adding remote {remote} {url}")
    cmd_status = subprocess.run(['git', 'remote', 'add', remote, url], capture_output=True)
    return cmd_status.returncode

def branch_mofify(branch_name):
    logging.debug(f"Modifying branch {branch_name}")
    cmd_status = subprocess.run(['git', 'branch', '-M', branch_name], capture_output=True)
    return cmd_status.returncode

def push_changes_branch(remote='origin', branch='master'):
    logging.debug(f"Pushing changes to {remote} {branch}")
    cmd_status = subprocess.run(['git', 'push', '-u', remote, branch],capture_output=True)
    return cmd_status.returncode

def fix_lfs_errors():
    logging.debug("Fixing LFS errors")
    list_branches = subprocess.run(['git', 'branch', '-a'],capture_output=True).stdout.decode('utf-8').split('\n')
    for branch in list_branches:
        logging.warning(f"Fixing LFS errors in branch {branch}")
        cmd_status = subprocess.run(['git', 'checkout', branch], capture_output=True)
        if cmd_status.returncode != 0:
            logging.error(f"Error checking out branch {branch}")
            return cmd_status.returncode
        cmd_status = subprocess.run(['git', 'lfs', 'install'], capture_output=True)
        if cmd_status.returncode != 0:
            logging.error(f"Error checking out branch {branch}")
            return cmd_status.returncode
        cmd_status = subprocess.run(['git', 'lfs', 'migrate', 'import','--above=50MB', '--include-ref={branch}'], capture_output=True)
        if cmd_status.returncode != 0:
            logging.error(f"Error checking out branch {branch}")
            return cmd_status.returncode
        cmd_status = subprocess.run(['git', 'push', '--force', 'origin', branch], capture_output=True)
        return cmd_status.returncode
