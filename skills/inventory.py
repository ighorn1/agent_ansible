"""
Skill INVENTORY — gestion de l'inventaire Ansible.

Usage LLM :
  SKILL:inventory ARGS:show
  SKILL:inventory ARGS:list              (hôtes avec variables)
  SKILL:inventory ARGS:hosts             (liste des hôtes)
  SKILL:inventory ARGS:groups            (liste des groupes)
  SKILL:inventory ARGS:add-host <ip> [groupe] [vars...]
  SKILL:inventory ARGS:add-group <nom>
  SKILL:inventory ARGS:remove-host <ip_ou_nom>
  SKILL:inventory ARGS:ping-all          (teste la connectivité)
  SKILL:inventory ARGS:facts <hôte>      (collecte les facts)
"""
import os
import re
import subprocess

DESCRIPTION = "Gestion de l'inventaire Ansible (hôtes, groupes, facts)"
USAGE = "SKILL:inventory ARGS:show | list | hosts | groups | add-host <ip> [groupe] | remove-host <hôte> | ping-all | facts <hôte>"

INVENTORY_FILE = "/opt/agent_ansible/inventory/hosts"
ANSIBLE_CFG    = "/opt/agent_ansible/ansible.cfg"


def _run(cmd: str, timeout: int = 60) -> str:
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
        return out[:4000] if out else "(aucune sortie)"
    except subprocess.TimeoutExpired:
        return f"Timeout ({timeout}s)"
    except Exception as e:
        return str(e)


def _read_inventory() -> str:
    if not os.path.exists(INVENTORY_FILE):
        return ""
    with open(INVENTORY_FILE) as f:
        return f.read()


def _write_inventory(content: str):
    os.makedirs(os.path.dirname(INVENTORY_FILE), exist_ok=True)
    with open(INVENTORY_FILE, "w") as f:
        f.write(content)


def run(args: str, context) -> str:
    parts = args.strip().split(None, 1)
    action = parts[0].lower() if parts else "show"
    rest   = parts[1] if len(parts) > 1 else ""

    if action == "show":
        content = _read_inventory()
        return content if content else f"Inventaire vide ou inexistant : {INVENTORY_FILE}"

    if action == "list":
        return _run(f"ansible-inventory -i {INVENTORY_FILE} --list 2>/dev/null || cat {INVENTORY_FILE}")

    if action == "hosts":
        return _run(f"ansible-inventory -i {INVENTORY_FILE} --list-hosts all 2>/dev/null")

    if action == "groups":
        return _run(f"ansible-inventory -i {INVENTORY_FILE} --list 2>/dev/null | python3 -c \"import json,sys; d=json.load(sys.stdin); print('\\n'.join(k for k in d if not k.startswith('_')))\"")

    if action == "add-host":
        rparts = rest.split()
        if not rparts:
            return "Précise l'IP ou le nom d'hôte."
        host  = rparts[0]
        group = rparts[1] if len(rparts) > 1 else "all"
        vars_ = " ".join(rparts[2:]) if len(rparts) > 2 else ""

        content = _read_inventory()
        lines   = content.splitlines() if content else []

        # Vérifie si le groupe existe déjà
        group_header = f"[{group}]"
        if group_header not in content:
            lines.append(f"\n{group_header}")

        # Ajoute l'hôte sous le groupe
        entry = f"{host} {vars_}".strip()
        if entry in content:
            return f"Hôte '{host}' déjà dans l'inventaire."

        # Insère après l'en-tête de groupe
        new_lines = []
        inserted  = False
        for line in lines:
            new_lines.append(line)
            if line.strip() == group_header and not inserted:
                new_lines.append(entry)
                inserted = True

        if not inserted:
            new_lines.append(entry)

        _write_inventory("\n".join(new_lines) + "\n")
        return f"Hôte '{host}' ajouté au groupe '{group}'."

    if action == "add-group":
        group = rest.strip()
        if not group:
            return "Précise le nom du groupe."
        content = _read_inventory()
        if f"[{group}]" in content:
            return f"Groupe '{group}' existe déjà."
        _write_inventory(content + f"\n[{group}]\n")
        return f"Groupe '{group}' créé."

    if action == "remove-host":
        host = rest.strip()
        if not host:
            return "Précise l'hôte à supprimer."
        content = _read_inventory()
        new_content = "\n".join(
            l for l in content.splitlines()
            if not l.strip().startswith(host)
        )
        _write_inventory(new_content + "\n")
        return f"Hôte '{host}' supprimé de l'inventaire."

    if action == "ping-all":
        return _run(f"ansible all -i {INVENTORY_FILE} -m ping", timeout=60)

    if action == "facts":
        host = rest.strip()
        if not host:
            return "Précise l'hôte."
        return _run(
            f"ansible {host} -i {INVENTORY_FILE} -m setup 2>/dev/null | head -80",
            timeout=30
        )

    return "Action inconnue. Disponible : show, list, hosts, groups, add-host, add-group, remove-host, ping-all, facts"
