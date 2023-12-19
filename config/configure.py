#!/usr/bin/env python3
"""
Usage:
  setup.py [--dev]
"""
from os import chdir
from os.path import dirname, realpath
from pathlib import Path
from docopt import docopt
from mako.template import Template

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
node_exporter_metrics_targets = {
    "montagu.vaccineimpact.org:9100": "montagu prod",
    "wpia-annex2.montagu.dide.ic.ac.uk:9100": "annex",
    "14.0.0.2": "reside-bk1",
    "14.0.0.3": "reside-bk2",
    "14.0.0.4": "reside-bk3",
    "14.0.0.5": "reside-bk4",
    "14.0.0.6": "reside-bk5",
    "14.0.0.7": "reside-bk6",
    "14.0.0.8": "reside-bk7",
    "14.0.0.9": "reside-bk8",
    "14.0.0.10": "reside-deploy1",
    "14.0.0.11": "reside-bk-browser-test1",
    "14.0.0.12": "reside-bk-multicore1",
    "14.0.0.13": "reside-bk-multicore2",
    "14.0.0.14": "reside-bk-multicore3"
}


def relabel_config(ip, target):
    return ['- targets: ["{}"]'.format(ip), '  labels: ', '    instance: "{}"'.format(target)]


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

    metrics_targets = []
    for ip, target in node_exporter_metrics_targets.items():
        metrics_targets += relabel_config(ip, target)

    Path('alertmanager').mkdir(exist_ok=True)
    instantiate_config(
        "alertmanager.template.yml",
        "alertmanager/alertmanager.yml",
        {"slack_oauth_token": vault.read_secret(slack_oauth_token),
         "slack_default_channel": slack_default_channel,
         "slack_hint_channel": slack_hint_channel}
    )
    instantiate_config(
        "prometheus.template.yml",
        "prometheus/prometheus.yml",
        {"aws_access_key_id": vault.read_secret("secret/vimc/prometheus/aws_access_key_id"),
         "aws_secret_key": vault.read_secret("secret/vimc/prometheus/aws_secret_key"),
         "metrics_targets": "\n      ".join(metrics_targets)}
    )
    with open("buildkite.env", 'w') as f:
        f.write("BUILDKITE_AGENT_TOKEN={}".format( \
            vault.read_secret("secret/buildkite/agent", "token")))
