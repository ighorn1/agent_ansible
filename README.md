# agent_ansible

Agent d'automatisation d'infrastructure via Ansible. Exécute des playbooks, lance des commandes ad-hoc sur un parc de serveurs, gère l'inventaire, les rôles Galaxy et les secrets Vault.

## Rôle

Cet agent est fait pour automatiser des tâches **sur plusieurs serveurs distants** via Ansible. Pour une tâche sur le serveur local uniquement, utiliser `agent_debian`.

## Installation

```bash
cd /opt/agent_ansible
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Ansible doit être installé sur le système
apt install ansible
systemctl enable --now agent_ansible
```

## Skills disponibles

| Skill | Description |
|-------|-------------|
| `playbook` | Exécute un playbook Ansible (`ansible-playbook`) |
| `adhoc` | Commandes ad-hoc sur un groupe d'hôtes (`ansible -m`) |
| `inventory` | Gestion de l'inventaire (list, add, remove, ping) |
| `galaxy` | Installation de rôles et collections (`ansible-galaxy`) |
| `vault` | Chiffrement/déchiffrement de secrets (`ansible-vault`) |
| `shell` | Commandes shell locales (utile pour diagnostics) |
| `script` | Bibliothèque de scripts bash (save/list/show/edit/exec/run/delete) |
| `agents_status` | Statut des agents du système |
| `mqtt_send` | Publication sur un topic MQTT |
| `mqtt_subscribe` | Souscription dynamique à un topic MQTT |
| `muc_send` | Message dans le groupe XMPP |

## Bibliothèque de scripts

Les scripts bash sont stockés dans `/opt/agent_ansible/scripts/`. Ils peuvent encapsuler des appels `ansible-playbook` ou des opérations de maintenance sur l'infra.

Les noms sont normalisés automatiquement (extensions strip, extensions système interdites). Le contenu doit contenir au moins une commande réelle.

## Structure

```
agent_ansible.py      — Point d'entrée
skills/               — 11 skills Ansible
scripts/              — Scripts bash persistants
config/               — Configuration et system prompt
playbooks/            — Playbooks Ansible
inventory/
  hosts               — Inventaire des hôtes
ansible.cfg           — Configuration Ansible
agent_ansible.service — Unit systemd
```

## Configuration

`config/config.json` :
```json
{
  "agent_id": "ansible.main",
  "xmpp": {
    "jid": "ansible.main@xmpp.ovh",
    "password": "...",
    "admin_jid": "sylvain@xmpp.ovh",
    "muc_room": "agents@muc.xmpp.ovh"
  },
  "mqtt": { "host": "localhost", "port": 1883 },
  "llm": {
    "base_url": "http://192.168.7.119:11434",
    "model": "qwen3:8b",
    "temperature": 0.3
  },
  "llm_profiles": {
    "local": "qwen3:8b",
    "cloud": "gpt-oss:120b-cloud"
  },
  "use_omemo": true,
  "use_llm_coordinator": true
}
```

## Commandes

```
/report   — Rapport (stats tâches + version Ansible)
/update   — Git pull + redémarrage du service
/status   — État de la queue de tâches
/script   — Gestion de la bibliothèque de scripts bash
```

## Exemples de tâches (via Nexus)

```
"Lance le playbook site.yml sur le groupe webservers"
"Fais un apt upgrade sur tous les serveurs de prod"
"Ping tous les hôtes de l'inventaire"
"Installe le rôle geerlingguy.nginx depuis Galaxy"
"Planifie le playbook backup.yml tous les soirs à 02:00"
```
