# AcmeBuddyCertificateNotLoaded

> [!NOTE]
> This alert is new and has not happened in practice yet. The playbook below is
> mostly speculative about what could go wrong.

A certificate was obtained by [acme-buddy][acme-buddy] but did not get loaded
by the relevant web server.

acme-buddy runs in a container alongside a web server (most often Nginx) and
automatically obtains certificates from Let's Encrypt when necessary. After
obtaining the certificate, acme-buddy writes it to a shared volume and sends a
SIGHUP signal to the web server instructing it to reload the certificate.

If the reload process fails for any reason, the web server might continue
serving the old certificate even as it approaches its expiry date. This
alert compares the certificate fingerprint as reported by acme-buddy and the
one received by [the blackbox probe][blackbox_exporter].

## Severity

Generally, this alert will trigger as soon as the certificate is renewed by
acme-buddy, which would be 30 days before expiry. This leaves a reasonable
amount of time to provide fix. More alerts (CertificateExpiry and eventually
BlackBoxProbeFailed) will start triggering closer to the expiry date.

It is however a sign of misconfiguration that needs to be addressed before it
becomes a more pressing issue.

## Diagnosis

### Certificate metadata

You can use the following command to fetch the certificate and compute its
fingerprint yourself, comparing it with the values exposed in the metrics:

```sh
openssl s_client -connect "NAME.dide.ic.ac.uk:443" 2>/dev/null </dev/null | openssl x509 -fingerprint -sha256 -noout
```

Adding the `-text` option will also print the full certificate's attributes,
including its issuance time (Not Before) and expiry (Not After).

### Container logs

The first step is to SSH to the machine hosting the service. Using `docker ps`,
identify the acme-buddy and the Web server containers at fault.

The commands below use wodin-dev as an example, but they should apply to any
acme-buddy deployment.
```sh
$ docker ps
CONTAINER ID   IMAGE                               [...]  NAMES
3669262abb3a   ghcr.io/reside-ic/acme-buddy:main   [...]  wodin-acme-buddy
7f11e59ec71b   mrcide/wodin-proxy:main             [...]  wodin-proxy
```

Next use `docker logs` on the acme-buddy container to find logs relevant to the
most recent certificate issuance:

```sh
$ docker logs wodin-acme-buddy
[INFO] [wodin-dev.dide.ic.ac.uk] acme: Obtaining bundled SAN certificate
[...]
[INFO] [wodin-dev.dide.ic.ac.uk] acme: Trying to solve DNS-01
[...]
[INFO] [wodin-dev.dide.ic.ac.uk] Server responded with a certificate.
reloading container wodin-proxy
certificate issued, next renewal in 1439h6m22.517963409s
```

The logs above show an example of the web server container being reloaded
successfully. If the alert is firing, the logs are likely to look different:

- The `reloading container` line is absent from the logs: acme-buddy was not
  configured to send any signal. Make sure the `-reload-container` flag was
  passed to it.
- acme-buddy cannot reach the docker daemon. acme-buddy uses the Docker API to
  send a signal to the web server container, and must therefore have access to
  the Docker socket. The Docker socket needs to be bind-mounted into the
  acme-buddy. See the [acme-buddy documentation][acme-reload] for more details.
  ```
  could not reload container: Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
  ```

- The name of the web server container is incorrect, or the web server
  container was not running at the time the certificate was issued. Compare the
  value passed to the `-reload-container` flag with the output of `docker ps`.
  If applicable, be mindful of docker compose's naming pattern (eg. using the
  right "project name" as a prefix to the container name, using dashes vs
  underscore depending on the version).
  ```
  could not reload container: Error response from daemon: cannot kill container: foobar: No such container: foobar
  ```

- The shared volume between acme-buddy and the web server is not configured
  properly and despite reloading its configuration, the web server does not see
  the new certificate.

  Check the `--certificate-path` and `--key-path` options of acme-buddy and the
  corresponding options of your web server. Make sure acme-buddy and the web
  server share the same volume.

  Use docker exec to inspect the certificate file from within the proxy container:
  ```sh
  docker exec wodin-proxy openssl x509 -fingerprint -sha256 -noout -in /run/proxy/cert.pem
  ```

You should check the logs of the web server, using `docker logs` once again.
Depending on the server's verbosity settings it may not print anything on a
successful reload, if the alert was caused by the web server failing to load
the configuration or certificates then it should be obvious from its logs.

### Manual reload

In the short term, reloading the web server manually should force it to reload
the certificate. This can be achieved by sending `SIGHUP` to the relevant
container or process.

```
docker kill -s SIGHUP wodin-proxy
```

If this works and resolves the alert then the issue was most likely in the
acme-buddy configuration, which would have been unable to send the signal
itself.

[acme-buddy]: https://github.com/reside-ic/acme-buddy
[acme-reload]: https://github.com/reside-ic/acme-buddy?tab=readme-ov-file#reloading-a-container
[blackbox_exporter]: https://github.com/prometheus/blackbox_exporter
