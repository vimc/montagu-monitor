#!/usr/bin/env python3
from os import chdir
from os.path import dirname, realpath
from pathlib import Path

from pystache import render

from vault.vault import VaultClient


def instantiate_config(template_path, target_path, values):
    print("Templating from {} to {}".format(template_path, target_path))
    with open(template_path, 'r') as f:
        template = f.read()
    with open(target_path, 'w') as f:
        f.write(render(template, values))


if __name__ == "__main__":
    # Set working directory to this script's dir
    chdir(dirname(realpath(__file__)))
    vault = VaultClient()

    Path('alertmanager').mkdir(exist_ok=True)
    instantiate_config(
        "alertmanager.template.yml",
        "alertmanager/alertmanager.yml",
        {"slack_webhook": vault.read_secret("secret/slack/monitor-webhook")}
    )