"""
Skill GALAXY — gestion des rôles et collections Ansible Galaxy.

Usage LLM :
  SKILL:galaxy ARGS:install <role_ou_collection>
  SKILL:galaxy ARGS:list
  SKILL:galaxy ARGS:remove <role>
  SKILL:galaxy ARGS:search <terme>
  SKILL:galaxy ARGS:info <role>
  SKILL:galaxy ARGS:init <nom_role>           (crée un squelette de rôle)
  SKILL:galaxy ARGS:collection install <nom>
  SKILL:galaxy ARGS:collection list
"""
import subprocess
import os

DESCRIPTION = "Gestion des rôles et collections Ansible Galaxy"
USAGE = "SKILL:galaxy ARGS:install <role> | list | remove <role> | search <terme> | info <role> | init <nom> | collection install <nom>"

ROLES_DIR = "/opt/agent_ansible/roles"


def _run(cmd: str, timeout: int = 60) -> str:
    env = os.environ.copy()
    env["ANSIBLE_FORCE_COLOR"] = "0"
    try:
        result = subprocess.run(
            cmd, shell=True, text=True,
            capture_output=True, timeout=timeout, env=env
        )
        out = (result.stdout + result.stderr).strip()
        return out[:4000] if out else "(aucune sortie)"
    except subprocess.TimeoutExpired:
        return f"Timeout ({timeout}s)"
    except Exception as e:
        return str(e)


def run(args: str, context) -> str:
    parts = args.strip().split(None, 1)
    action = parts[0].lower() if parts else "list"
    rest   = parts[1] if len(parts) > 1 else ""

    if action == "install":
        if not rest:
            return "Précise le rôle ou la collection à installer."
        return _run(f"ansible-galaxy install {rest} --roles-path {ROLES_DIR}", timeout=120)

    if action == "list":
        return _run(f"ansible-galaxy list --roles-path {ROLES_DIR}")

    if action == "remove":
        if not rest:
            return "Précise le rôle à supprimer."
        return _run(f"ansible-galaxy remove {rest} --roles-path {ROLES_DIR}")

    if action == "search":
        if not rest:
            return "Précise le terme de recherche."
        return _run(f"ansible-galaxy search {rest} | head -30")

    if action == "info":
        if not rest:
            return "Précise le rôle."
        return _run(f"ansible-galaxy info {rest}")

    if action == "init":
        if not rest:
            return "Précise le nom du rôle à créer."
        os.makedirs(ROLES_DIR, exist_ok=True)
        return _run(f"ansible-galaxy init {rest} --init-path {ROLES_DIR}")

    if action == "collection":
        parts2 = rest.split(None, 1)
        sub    = parts2[0].lower() if parts2 else "list"
        carg   = parts2[1] if len(parts2) > 1 else ""
        if sub == "install":
            return _run(f"ansible-galaxy collection install {carg}", timeout=120)
        if sub == "list":
            return _run("ansible-galaxy collection list")
        return f"Sous-commande inconnue : collection {sub}"

    return "Action inconnue. Disponible : install, list, remove, search, info, init, collection"
