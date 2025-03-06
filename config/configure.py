#!/usr/bin/env python3
"""
Usage:
  setup.py [--dev]
"""
from os import chdir, makedirs
from os.path import dirname, realpath
from pathlib import Path
from docopt import docopt
from mako.template import Template
import json
import os.path

from vault.vault import VaultClient

# This turns a very succinct JSON inventory of machines into something
# ingestable by Prometheus' file_sd mechanism. It uses the key as the
# instance label and the value as the target.
def process_inventory(name):
    with open(os.path.join("prometheus/data", name)) as f:
        nodes = json.load(f)

    targets = [ {
        "targets": [ ip ],
        "labels": { "instance": name }
    } for name, ip in nodes.items() ]

    os.makedirs("prometheus/generated", exist_ok=True)
    with open(os.path.join("prometheus/generated", name), "w") as f:
        json.dump(targets, f)


def instantiate_config(template_path, target_path, values):
    print("Templating from {} to {}".format(template_path, target_path))
    with open(template_path, 'r') as f:
        template = Template(f.read())
    with open(target_path, 'w') as f:
        f.write(template.render(**values))


def buildkite_node_exporter_config(name, ip):
    return {
        "targets": [ ip ],
        "labels": {
            "instance": name
        }
    }


if __name__ == "__main__":
    # Set working directory to this script's dir
    chdir(dirname(realpath(__file__)))
    vault = VaultClient()

    args = docopt(__doc__)
    if args["--dev"]:
        slack_default_channel = "monitor-test"
        slack_hint_channel = "monitor-test"
    else:
        slack_default_channel = "montagu-monitor"
        slack_hint_channel = "hint-monitor"

    slack_oauth_token = "secret/vimc/slack/oauth-token"

    process_inventory("hpc-windows-nodes.json")
    process_inventory("buildkite-nodes.json")

    Path('alertmanager').mkdir(exist_ok=True)
    instantiate_config(
        "alertmanager.template.yml",
        "alertmanager/alertmanager.yml",
        {"slack_oauth_token": vault.read_secret(slack_oauth_token),
         "slack_default_channel": slack_default_channel,
         "slack_hint_channel": slack_hint_channel}
    )
    instantiate_config(
        "grafana/grafana.template.ini",
        "grafana/grafana.ini",
        {"admin_password": vault.read_secret("secret/vimc/prometheus/grafana_password")}
    )

    print("Writing SSL certificate and key")
    makedirs("nginx", exist_ok=True)
    with open("nginx/certificate.pem", "w") as f:
        f.write(vault.read_secret("secret/bots/ssl", field="cert"))
    with open("nginx/key.pem", "w") as f:
        f.write(vault.read_secret("secret/bots/ssl", field="key"))
    with open("buildkite.env", 'w') as f:
        f.write("BUILDKITE_AGENT_TOKEN={}".format(
            vault.read_secret("secret/buildkite/agent", "token")))
    with open("prometheus/env", 'w') as f:
        f.write("AWS_ACCESS_KEY_ID={}\n".format(
            vault.read_secret("secret/vimc/prometheus/aws_access_key_id")))
        f.write("AWS_SECRET_ACCESS_KEY={}\n".format(
            vault.read_secret("secret/vimc/prometheus/aws_secret_key")))
