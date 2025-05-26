import os
import datetime
from git import Repo

# Directory
repo = os.getcwd()  # Obtiene el directorio actual

# Inactive branches older than ... days
dias = 60

# Protected branches
ramas_protegidas = ["master", "development", "staging"]

def ramas_inactivas(repo_path, dias, ramas_protegidas):
    repo = Repo(repo_path)
    tiempoActual = datetime.datetime.now(datetime.timezone.utc)
    fecha = tiempoActual - datetime.timedelta(days=dias)

    # Update remote references
    repo.git.fetch("--prune")

    # List to store branches that will be deleted
    ramas_a_eliminar = []

    # Iterate over remote branches
    for branch in repo.remote().refs:
        branch_name = branch.name.split("/")[-1]

        # Skip protected branches or those starting with "hotfix/"
        if branch_name in ramas_protegidas or branch_name.startswith("hotfix/"):
            print(f"Skipping protected branch: {branch_name}")
            continue

        # Get the last commit date
        last_commit_date = branch.commit.committed_datetime

        # Check if the branch is inactive
        if last_commit_date < fecha:
            print(f"Branch '{branch_name}' is inactive since {last_commit_date}.")
            ramas_a_eliminar.append((branch_name, last_commit_date))

    # Process branches to delete
    for branch_name, last_commit_date in ramas_a_eliminar:
        print(f"Processing branch '{branch_name}'...")

        # Create a local backup of the branch
        try:
            print(f"Creating a local backup for branch '{branch_name}'...")
            repo.git.checkout(branch_name, b=f"backup/{branch_name}")
            print(f"Backup created for branch '{branch_name}' as 'backup/{branch_name}'.")
        except Exception as e:
            print(f"Failed to create backup for branch '{branch_name}': {e}")
            continue

        # Delete the branch remotely
        try:
            print(f"Deleting branch '{branch_name}'...")
            repo.git.push("origin", "--delete", branch_name)
            print(f"Deleted branch '{branch_name}' successfully.")
        except Exception as e:
            print(f"Failed to delete branch '{branch_name}': {e}")

    print("\nSummary:")
    if ramas_a_eliminar:
        print("The following branches were deleted and backed up:")
        for branch_name, last_commit_date in ramas_a_eliminar:
            print(f"- {branch_name} (last commit: {last_commit_date})")
    else:
        print("No branches were deleted.")

if __name__ == "__main__":
    ramas_inactivas(repo, dias, ramas_protegidas)
# restaurar una rama eliminada  
# git checkout backip/nombre_rama 