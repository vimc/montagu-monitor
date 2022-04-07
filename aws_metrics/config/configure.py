#!/usr/bin/env python3
from os import chdir
from os.path import dirname, realpath
from pathlib import Path

from vault.vault import VaultClient

template = """[default]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
"""

vault = VaultClient()
secrets = {
    "access_key": vault.read_secret("secret/vimc/backup/aws_access_key_id"),
    "secret_key": vault.read_secret("secret/vimc/backup/aws_secret_access_key"),
}

# Set working directory to this script's dir
chdir(dirname(realpath(__file__)))

print("Writing out AWS credentials")
Path('volume').mkdir(exist_ok=True)
with open('volume/credentials', 'w') as f:
    f.write(template.format(**secrets))
