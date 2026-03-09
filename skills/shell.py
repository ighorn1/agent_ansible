"""
Skill SHELL — commandes shell et ansible directes (fallback).

Usage LLM : SKILL:shell ARGS:<commande>
"""
import subprocess

DESCRIPTION = "Exécution de commandes shell et ansible directes (fallback)"
USAGE = "SKILL:shell ARGS:<commande bash ou ansible>"


def run(args: str, context) -> str:
    cmd = args.strip()
    if not cmd:
        return "Commande vide."
    try:
        result = subprocess.run(
            cmd, shell=True, text=True,
            capture_output=True, timeout=120,
            executable="/bin/bash"
        )
        out = (result.stdout + result.stderr).strip()
        if len(out) > 4000:
            out = out[:4000] + "\n... [tronqué]"
        return out or f"(code retour : {result.returncode})"
    except subprocess.TimeoutExpired:
        return "Timeout (120s)"
    except Exception as e:
        return str(e)
