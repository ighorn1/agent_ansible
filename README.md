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
| `agents_status` | Statut des agents du système |
| `mqtt_send` | Publication sur un topic MQTT |
| `mqtt_subscribe` | Souscription dynamique à un topic MQTT |
| `muc_send` | Message dans le groupe XMPP |

## Structure

```
agent_ansible.py      — Point d'entrée
skills/               — 10 skills Ansible
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
    "model": "ministral-3:latest",
    "temperature": 0.3
  },
  "llm_profiles": {
    "local": "ministral-3:latest",
    "cloud": "gpt-oss:120b-cloud"
  }
}
```

## Commandes

```
/report   — Rapport (stats tâches + version Ansible)
/update   — Git pull + redémarrage du service
/status   — État de la queue de tâches
```

## Exemples de tâches (via Nexus)

```
"Lance le playbook site.yml sur le groupe webservers"
"Fais un apt upgrade sur tous les serveurs de prod"
"Ping tous les hôtes de l'inventaire"
"Installe le rôle geerlingguy.nginx depuis Galaxy"
```
