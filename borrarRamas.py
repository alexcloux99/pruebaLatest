import os
import datetime
from git import Repo

# Notes:
# 
# Commands:
# - To restore a deleted branch:
#   git checkout backup/branch_name
# - To list all backup branches:
#   git branch | findstr backup/
# - To delete a specific backup branch:
#   git branch -D backup/branch_name
# - To delete all backup branches:
#   git branch | grep "backup/" | xargs -I {} git branch -D {}
# - To clean up repository storage after branch deletion:
#   git gc --prune=now --aggressive

# Define the path to the Git repository.
repo_path = os.path.abspath(os.path.join(os.getcwd(), ".."))

# Branches with no commits in the last ..... days will be considered inactive.
inactive_days_threshold = 90

protected_branches = ["master", "development", "staging"]

def is_merged(repo, branch_name, protected_branches):
    for protected_branch in protected_branches:
        try:
            merge_base = repo.git.merge_base(f"origin/{branch_name}", f"origin/{protected_branch}")
            branch_commit = repo.git.rev_parse(f"origin/{branch_name}")
            if merge_base == branch_commit:
                print(f"Branch '{branch_name}' is merged into '{protected_branch}'.")
                return True
        except Exception as e:
            print(f"Error checking merge status for branch '{branch_name}' against '{protected_branch}': {e}")
    return False

def delete_inactive_branches(repo_path, inactive_days_threshold, protected_branches):
    repo = Repo(repo_path)
    current_time = datetime.datetime.now(datetime.timezone.utc)
    cutoff_date = current_time - datetime.timedelta(days=inactive_days_threshold)
    print("Loading...")
    repo.git.fetch("--prune")
    branches_to_delete = []
    for branch in repo.remote().refs:
        branch_name = branch.name.split("/", 1)[-1]

        # Skip branches that are protected
        if branch_name in protected_branches:
            print(f"Skipping protected branch: {branch_name}")
            continue

        # Check the last commit date
        last_commit_date = branch.commit.committed_datetime
        if last_commit_date < cutoff_date:
            print(f"Branch '{branch_name}' is inactive since {last_commit_date}.")

            # Check if the branch is merged into any protected branch
            if not is_merged(repo, branch_name, protected_branches):
                print(f"Branch '{branch_name}' is NOT merged into any protected branch skipping deletion.")
                continue

            branches_to_delete.append((branch_name, last_commit_date))

    for branch_name, last_commit_date in branches_to_delete:
        print(f"Processing branch '{branch_name}'...")

        # Create a local backup of the branch before deletion
        try:
            print(f"Creating a local backup for branch '{branch_name}'...")
            repo.git.checkout("-b", f"backup/{branch_name}", f"origin/{branch_name}")
            print(f"Backup created for branch '{branch_name}' as 'backup/{branch_name}'.")
        except Exception as e:
            print(f"Failed to create backup for branch '{branch_name}': {e}")
            continue

        # Delete the branch from the remote repository.
        try:
            print(f"Deleting branch '{branch_name}'...")
            repo.git.push("origin", "--delete", branch_name)
            print(f"Branch '{branch_name}' deleted successfully")
        except Exception as e:
            print(f"Failed to delete branch '{branch_name}': {e}")

    print("\nSummary:")
    if branches_to_delete:
        print("The following branches were deleted and backed up:")
        for branch_name, last_commit_date in branches_to_delete:
            print(f"- {branch_name} (last commit: {last_commit_date})")
    else:
        print("No branches were deleted.")

if __name__ == "__main__":
    delete_inactive_branches(repo_path, inactive_days_threshold, protected_branches)