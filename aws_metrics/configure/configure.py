#!/usr/bin/env python3

from vault import VaultClient

template = """[default]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
"""

vault = VaultClient()
secrets = {
    "access_key": vault.read_secret("secret/backup/aws_access_key_id"),
    "secret_key": vault.read_secret("secret/backup/aws_secret_access_key"),
}

print(template.format(**secrets))
