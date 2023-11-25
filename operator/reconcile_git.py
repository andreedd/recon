import os
import git


def is_remote_up_to_date(repo_path):
    repo = git.Repo(repo_path)
    remote_branch = repo.remote().refs[repo.active_branch.name]

    # Fetch the latest changes from the remote repository
    repo.remote().fetch()

    # Compare the local and remote commit hashes
    local_commit = repo.commit()
    remote_commit = remote_branch.commit

    return local_commit == remote_commit


def sync_remote_repository(repo_path):
    repo = git.Repo(repo_path)
    remote_branch = repo.remote().refs[repo.active_branch.name]

    # Fetch the latest changes from the remote repository
    repo.remote().fetch()

    # If not up to date, pull changes from the remote
    if not is_remote_up_to_date(repo_path):
        repo.git.pull(remote_branch.remote_name, repo.active_branch)


def reconcile():
    # Get the parent directory of the directory containing the script
    script_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))

    local_repo_path = parent_dir

    if not is_remote_up_to_date(local_repo_path):
        sync_remote_repository(local_repo_path)
        print("Repository synchronized.")
    else:
        print("Repository is already up to date.")


if __name__ == '__main__':
    reconcile()
