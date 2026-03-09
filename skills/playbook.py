"""
Skill PLAYBOOK — exécution et gestion de playbooks Ansible.

Usage LLM :
  SKILL:playbook ARGS:run <fichier.yml> [--limit <hôtes>] [--tags <tags>] [--extra-vars "k=v"]
  SKILL:playbook ARGS:check <fichier.yml>       (dry-run)
  SKILL:playbook ARGS:list                       (liste les playbooks disponibles)
  SKILL:playbook ARGS:show <fichier.yml>         (affiche le contenu)
  SKILL:playbook ARGS:create <nom> | <contenu>   (crée un nouveau playbook)
  SKILL:playbook ARGS:syntax <fichier.yml>       (vérifie la syntaxe)
"""
import os
import subprocess

DESCRIPTION = "Exécution et gestion de playbooks Ansible"
USAGE = "SKILL:playbook ARGS:run <fichier.yml> [--limit <hôtes>] [--tags <tags>] | check <fichier> | list | show <fichier> | create <nom>|<contenu> | syntax <fichier>"

PLAYBOOKS_DIR = "/opt/agent_ansible/playbooks"
INVENTORY     = "/opt/agent_ansible/inventory/hosts"
ANSIBLE_CFG   = "/opt/agent_ansible/ansible.cfg"


def _run(cmd: str, timeout: int = 300) -> str:
    env = os.environ.copy()
    env["ANSIBLE_FORCE_COLOR"] = "0"
    env["ANSIBLE_HOST_KEY_CHECKING"] = "False"
    if os.path.exists(ANSIBLE_CFG):
        env["ANSIBLE_CONFIG"] = ANSIBLE_CFG
    try:
        result = subprocess.run(
            cmd, shell=True, text=True,
            capture_output=True, timeout=timeout, env=env
        )
        out = (result.stdout + result.stderr).strip()
        return out[:5000] if out else "(aucune sortie)"
    except subprocess.TimeoutExpired:
        return f"Timeout ({timeout}s) — playbook trop long."
    except Exception as e:
        return str(e)


def _resolve_playbook(name: str) -> str:
    """Résout le chemin d'un playbook (relatif ou absolu)."""
    if os.path.isabs(name) and os.path.exists(name):
        return name
    # Cherche dans le dossier playbooks
    candidates = [
        os.path.join(PLAYBOOKS_DIR, name),
        os.path.join(PLAYBOOKS_DIR, name + ".yml"),
        os.path.join(PLAYBOOKS_DIR, name + ".yaml"),
        name,
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def run(args: str, context) -> str:
    parts = args.strip().split(None, 1)
    action = parts[0].lower() if parts else "list"
    rest   = parts[1] if len(parts) > 1 else ""

    if action == "list":
        files = []
        for d in [PLAYBOOKS_DIR]:
            if os.path.isdir(d):
                for f in sorted(os.listdir(d)):
                    if f.endswith((".yml", ".yaml")):
                        files.append(os.path.join(d, f))
        return "\n".join(files) if files else f"Aucun playbook dans {PLAYBOOKS_DIR}"

    if action == "show":
        path = _resolve_playbook(rest.strip())
        if not path:
            return f"Playbook '{rest.strip()}' introuvable."
        with open(path) as f:
            return f.read()[:3000]

    if action == "create":
        if "|" not in rest:
            return "Format : create <nom> | <contenu YAML>"
        name, content = rest.split("|", 1)
        name = name.strip()
        if not name.endswith((".yml", ".yaml")):
            name += ".yml"
        path = os.path.join(PLAYBOOKS_DIR, name)
        os.makedirs(PLAYBOOKS_DIR, exist_ok=True)
        with open(path, "w") as f:
            f.write(content.strip().replace("\\n", "\n"))
        return f"Playbook créé : {path}"

    if action in ("run", "check", "syntax"):
        # Parse : <fichier.yml> [options...]
        rparts = rest.split()
        if not rparts:
            return "Précise le fichier playbook."

        playbook_arg = rparts[0]
        options      = " ".join(rparts[1:]) if len(rparts) > 1 else ""

        path = _resolve_playbook(playbook_arg)
        if not path:
            return f"Playbook '{playbook_arg}' introuvable dans {PLAYBOOKS_DIR}"

        inv_flag = f"-i {INVENTORY}" if os.path.exists(INVENTORY) else ""

        if action == "syntax":
            cmd = f"ansible-playbook {inv_flag} --syntax-check {path}"
        elif action == "check":
            cmd = f"ansible-playbook {inv_flag} --check {path} {options}"
        else:
            cmd = f"ansible-playbook {inv_flag} {path} {options}"

        return _run(cmd, timeout=600)

    return "Action inconnue. Disponible : run, check, syntax, list, show, create"
