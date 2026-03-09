"""
Skill ADHOC — commandes Ansible ad-hoc sur l'inventaire.

Usage LLM :
  SKILL:adhoc ARGS:<hôtes> <module> [args]
  SKILL:adhoc ARGS:all ping
  SKILL:adhoc ARGS:webservers shell cmd="uptime"
  SKILL:adhoc ARGS:192.168.1.10 command cmd="df -h"
  SKILL:adhoc ARGS:all setup filter="ansible_memory_mb"
  SKILL:adhoc ARGS:all apt name=nginx state=present
  SKILL:adhoc ARGS:all service name=nginx state=restarted
"""
import os
import subprocess

DESCRIPTION = "Commandes Ansible ad-hoc sur les hôtes de l'inventaire"
USAGE = "SKILL:adhoc ARGS:<hôtes> <module> [args]  — Ex: all ping | webservers shell cmd='uptime' | all apt name=nginx state=present"

INVENTORY   = "/opt/agent_ansible/inventory/hosts"
ANSIBLE_CFG = "/opt/agent_ansible/ansible.cfg"

# Modules courants et leurs alias simplifiés
MODULE_ALIASES = {
    "ping":    ("ping", ""),
    "uptime":  ("shell", "cmd='uptime'"),
    "df":      ("shell", "cmd='df -h'"),
    "free":    ("shell", "cmd='free -h'"),
    "whoami":  ("shell", "cmd='whoami'"),
    "reboot":  ("reboot", ""),
    "gather":  ("setup", ""),
}


def _run(cmd: str, timeout: int = 120) -> str:
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
        return f"Timeout ({timeout}s)"
    except Exception as e:
        return str(e)


def run(args: str, context) -> str:
    parts = args.strip().split(None, 2)
    if len(parts) < 2:
        return (
            "Format : SKILL:adhoc ARGS:<hôtes> <module> [args]\n"
            "Exemple : all ping | webservers shell cmd='df -h'"
        )

    hosts  = parts[0]
    module = parts[1].lower()
    margs  = parts[2] if len(parts) > 2 else ""

    # Alias pratiques
    if module in MODULE_ALIASES and not margs:
        module, margs = MODULE_ALIASES[module]

    inv_flag = f"-i {INVENTORY}" if os.path.exists(INVENTORY) else "-i localhost,"

    # Construction de la commande
    cmd = f"ansible {hosts} {inv_flag} -m {module}"
    if margs:
        cmd += f" -a \"{margs}\""

    return _run(cmd)
