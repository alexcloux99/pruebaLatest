import os
import datetime
from git import Repo
# Url del repositorio 
repo = ""
# Dias de inactividad para elminar las ramas
dias = 60
# Ramas que no se eliminan 
ramas_protegidas = ["master", "development", "staging"]

def ramas_inactivas(repo_path, dias, ramas_protegidas):
    repo = Repo(repo_path)
    tiempoActual = datetime.datetime.tiempoActual()
    fecha = tiempoActual - datetime.timedelta(days=dias)

    # Actualizar las referencias remotas
    repo.git.fetch("--prune")

    # Iterar sobre las ramas remotas
    for branch in repo.remote().refs:
        branch_name = branch.name.split("/")[-1]

        # Saltar ramas protegidas o que comienzan con "hotfix/"
        if branch_name in ramas_protegidas or branch_name.startswith("hotfix/"):
            print(f"Skipping protected branch: {branch_name}")
            continue

        # Obtener la fecha del último commit
        last_commit_date = branch.commit.committed_datetime

        # Verificar si la rama está inactiva
        if last_commit_date < fecha:
            print(f"Branch '{branch_name}' is inactive since {last_commit_date}. Deleting...")
            try:
                # Eliminar la rama remotamente
                repo.git.push("origin", "--delete", branch_name)
                print(f"Deleted branch '{branch_name}' successfully.")
            except Exception as e:
                print(f"Failed to delete branch '{branch_name}': {e}")

if __name__ == "__main__":
    ramas_inactivas(repo, dias, ramas_protegidas)