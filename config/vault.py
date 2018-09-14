import os

import hvac

DEFAULT_VAULT_ADDR = "https://support.montagu.dide.ic.ac.uk:8200"


class VaultClient(object):
    def __init__(self):
        self.client = None

    def _connect(self):
        vault_url = os.environ.get("VAULT_ADDR", DEFAULT_VAULT_ADDR)
        vault_token = os.environ.get("VAULT_AUTH_GITHUB_TOKEN")
        if not vault_token:
            raise Exception("Missing vault token. Please export VAULT_AUTH_GITHUB_TOKEN")
        self.client = hvac.Client(url=vault_url)
        self.client.auth_github(vault_token)

    def read_secret(self, path, field='value'):
        if not self.client:
            self._connect()
        secret = self.client.read(path)
        return secret['data'][field]
