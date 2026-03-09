"""
Skill VAULT — gestion des secrets Ansible Vault.

Usage LLM :
  SKILL:vault ARGS:encrypt <fichier>
  SKILL:vault ARGS:decrypt <fichier>
  SKILL:vault ARGS:view <fichier>
  SKILL:vault ARGS:encrypt-string <valeur> <nom_variable>
  SKILL:vault ARGS:rekey <fichier>
"""
import os
import subprocess

DESCRIPTION = "Gestion des secrets chiffrés avec Ansible Vault"
USAGE = "SKILL:vault ARGS:encrypt <fichier> | decrypt <fichier> | view <fichier> | encrypt-string <valeur> <nom_var>"

VAULT_PASS_FILE = "/opt/agent_ansible/config/.vault_pass"


def _run(cmd: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, text=True,
            capture_output=True, timeout=timeout
        )
        out = (result.stdout + result.stderr).strip()
        return out[:3000] if out else "(aucune sortie)"
    except Exception as e:
        return str(e)


def _vault_flag() -> str:
    if os.path.exists(VAULT_PASS_FILE):
        return f"--vault-password-file {VAULT_PASS_FILE}"
    return "--ask-vault-pass"


def run(args: str, context) -> str:
    parts = args.strip().split(None, 1)
    action = parts[0].lower() if parts else ""
    rest   = parts[1] if len(parts) > 1 else ""

    flag = _vault_flag()

    if action == "encrypt":
        if not rest:
            return "Précise le fichier à chiffrer."
        return _run(f"ansible-vault encrypt {flag} {rest}")

    if action == "decrypt":
        if not rest:
            return "Précise le fichier à déchiffrer."
        return _run(f"ansible-vault decrypt {flag} {rest}")

    if action == "view":
        if not rest:
            return "Précise le fichier à visualiser."
        return _run(f"ansible-vault view {flag} {rest}")

    if action == "encrypt-string":
        parts2 = rest.split(None, 1)
        if len(parts2) < 2:
            return "Format : encrypt-string <valeur> <nom_variable>"
        value, name = parts2[0], parts2[1]
        return _run(f"ansible-vault encrypt_string {flag} '{value}' --name '{name}'")

    if action == "rekey":
        if not rest:
            return "Précise le fichier."
        return _run(f"ansible-vault rekey {flag} {rest}")

    if action == "set-password":
        # Définir le mot de passe du vault (stocké dans .vault_pass)
        password = rest.strip()
        if not password:
            return "Précise le mot de passe."
        with open(VAULT_PASS_FILE, "w") as f:
            f.write(password)
        os.chmod(VAULT_PASS_FILE, 0o600)
        return f"Mot de passe vault enregistré dans {VAULT_PASS_FILE}"

    return "Action inconnue. Disponible : encrypt, decrypt, view, encrypt-string, rekey, set-password"
