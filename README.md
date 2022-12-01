# Montagu monitor
Monitoring and alerts for Montagu and supporting services.

We should consider separating out the Montagu-specific bits.

This repo of a Docker Compose configuration that spins up a
[Prometheus](https://prometheus.io/) instance with an accompanying alert
manager. These instances are configured by:

* `prometheus.yml` - Main config (see [docs](https://prometheus.io/docs/prometheus/latest/configuration/configuration/))
* `alert-rules.yml` - What conditions should trigger alerts (see [docs](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/))
* `alertmanager.yml` - Alertmanager config. This controls where alerts get posted to (see [docs](https://prometheus.io/docs/alerting/configuration/))

To start the monitor and external metric exporters (see below) use:

```
pip3 install -r requirements.txt --user
./run
```

To reload Prometheus and the alert manager after a config change, run
```
./reload
```

## Local development
To run locally and have the alert manager notify a test Slack channel rather than creating noise in
the real monitor channel, use
```
./run --dev
```

and for reloading
```
./reload --dev
```

To force alerts to fire just invert the rules in `prometheus/alert-rules.yml` temporarily, e.g. change a rule expression
like

`up{job="bb8"} == 0`

to

`up{job="bb8"} == 1`


## Deployment on support

Connect as the `montagu` user on support (either by connecting with `ssh montagu@support.dide.ic.ac.uk` or by using `sudo su montagu`, then)

```
# git clone --recursive https://github.com/vimc/montagu-monitor monitor
cd ~/monitor
git pull
```

And then either call `./run` (if there are code changes) or `./reload` (to
refresh the config).

## Metric exporters
Prometheus relies on the services it is monitoring serving up a text file that
exports values to monitor. By convention, these are served at
`SERVICE_URL/metrics`, and each line follows this syntax:

```
<metric name>{<label name>=<label value>, ...} <metric value>
```

### Internal metric exporters
The intention is that we will add `/metric` endpoints to our various apps,
either:

* Using existing metrics endpoints built-in to things like Docker Daemon (see
  [list](https://prometheus.io/docs/instrumenting/exporters/#software-exposing-prometheus-metrics))
* Using existing "exporters", that sit alongside in a separate docker container,
  like the one for Postgres (see [list](https://prometheus.io/docs/instrumenting/exporters/#third-party-exporters))
* Directly integrated into the app (using one of the
  [client libraries](https://prometheus.io/docs/instrumenting/clientlibs/))
* Write our own exporter to sit alongside as a small Flask app in a separate
  container

### External metric exporters
For monitoring external services (like S3) there's no need to deploy them
separately; instead we can deploy them alongside Prometheus. So far we have one:
`aws_metrics`. When you run `run` it will also build and start the exporter.

### Machine metrics

See [machine-metrics](https://github.com/vimc/machine-metrics) for turning on Prometheus Node Exporter for publishing machine metrics from a system. This will make the metrics accessible on `localhost:9100`. You then need to add a new job to `prometheus.yml` to pull metrics, they can then be used to build alerts or for graphs.
