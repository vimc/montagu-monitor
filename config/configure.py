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

from vault.vault import VaultClient


def instantiate_config(template_path, target_path, values):
    print("Templating from {} to {}".format(template_path, target_path))
    with open(template_path, 'r') as f:
        template = Template(f.read())
    with open(target_path, 'w') as f:
        f.write(template.render(**values))


# Not amazing that we have to write this here duplicating the IP
# setup done on the hyperv machine. But this needs to be defined
# somewhere as we can't use data from after the scraping in the
# rename config. And having this here is a bit more explicit than
# having the renaming done in grafana
buildkite_hosts = {
    "reside-bk1": "14.0.0.2:9100",
    "reside-bk2": "14.0.0.3:9100",
    "reside-bk3": "14.0.0.4:9100",
    "reside-bk4": "14.0.0.5:9100",
    "reside-bk5": "14.0.0.6:9100",
    "reside-bk6": "14.0.0.7:9100",
    "reside-bk7": "14.0.0.8:9100",
    "reside-bk8": "14.0.0.9:9100",
    "reside-deploy1": "14.0.0.10:9100",
    "reside-bk-browser-test1": "14.0.0.11:9100",
    "reside-bk-multicore1": "14.0.0.12:9100",
    "reside-bk-multicore2": "14.0.0.13:9100",
    "reside-bk-multicore3": "14.0.0.14:9100",
}


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

    buildkite_targets = [
        buildkite_node_exporter_config(name, ip)
        for name, ip in buildkite_hosts.items()
    ]

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
    with open("prometheus/machine-metrics.json", "w") as f:
        json.dump(buildkite_targets, f)
