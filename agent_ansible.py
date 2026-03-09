#!/usr/bin/env python3
"""
Agent Ansible — Automatisation d'infrastructure via Ansible.
Gère playbooks, commandes ad-hoc, inventaire, galaxy, vault.
"""
import os
import sys
import logging


from agents_core import BaseAgent, AgentContext, Message, MessageType

logger = logging.getLogger(__name__)


class AgentAnsible(BaseAgent):
    AGENT_TYPE = "ansible"
    DESCRIPTION = (
        "Automatisation infrastructure multi-serveurs via Ansible : "
        "exécuter des playbooks, lancer des commandes ad-hoc sur plusieurs machines, "
        "gérer l'inventaire des hôtes, installer des rôles Galaxy, gérer les secrets Vault. "
        "À utiliser pour automatiser des tâches sur un parc de serveurs distants."
    )
    DEFAULT_CONFIG_PATH = "/opt/agent_ansible/config/config.json"

    def get_skills_dir(self) -> str:
        return os.path.join(os.path.dirname(__file__), "skills")

    def on_start(self):
        self.mqtt.send_to("nexus", f"Agent Ansible ({self.agent_id}) en ligne.")

    def setup_extra_subscriptions(self):
        self.mqtt.subscribe(
            f"agents/{self.agent_id}/control",
            self._on_control,
        )

    def _on_control(self, msg, topic: str):
        from agents_core.message_bus import Message as Msg
        payload = msg.payload if isinstance(msg, Msg) else str(msg)
        result = self._handle_system_command(payload)
        if result and isinstance(msg, Msg):
            self.mqtt.reply(msg, result)

    def handle_custom_command(self, cmd: str, args: str, source_msg=None):
        if cmd == "report":
            return self._build_report()
        if cmd == "update":
            return self._self_update()
        return f"Commande inconnue : /{cmd}"

    def on_broadcast(self, msg: Message):
        if "status" in str(msg.payload).lower():
            self.mqtt.reply(msg, self._build_report())

    def _build_report(self) -> str:
        import subprocess
        stats = self.queue.daily_stats()
        lines = [f"── Rapport {self.agent_id} ──"]
        lines.append(
            f"Tâches : {stats['total']} total / "
            f"{stats['completed']} OK / {stats['failed']} erreurs / "
            f"durée moy. {stats['avg_duration_s']}s"
        )
        try:
            version = subprocess.check_output(
                "ansible --version | head -1", shell=True, text=True
            ).strip()
            lines.append(f"Ansible : {version}")
        except Exception:
            pass
        return "\n".join(lines)

    def _self_update(self) -> str:
        import subprocess
        try:
            out = subprocess.check_output(
                "cd /opt/agent_ansible && git pull",
                shell=True, text=True, stderr=subprocess.STDOUT
            )
            subprocess.Popen(["systemctl", "restart", self.agent_id])
            return f"Mise à jour :\n{out}\nRedémarrage..."
        except subprocess.CalledProcessError as e:
            return f"Erreur : {e.output}"


if __name__ == "__main__":
    AgentAnsible().run()
