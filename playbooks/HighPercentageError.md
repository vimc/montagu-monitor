# HighPercentageError

This error is triggered for a container when over 5% of its logs in a 5-minute period contain the (case-insensitive) text 'error' (excepting errors that we have deemed wontfix).

When a new error starts alerting, it should be triaged. The alert may be temporarily silenced, though this risks our failing to be alerted about different errors from the same instance (see below for guidance). Some of the time, we will deliberately choose to do nothing about an error, if e.g. it is a false positive or not worth fixing; in this case, we have a way to permanently ignore by matching the log message (see below for guidance).

You can also decide to adjust the sensitivity of the alert by changing the duration or threshold in `./config/loki/alert-rules.template.yml`. This has a global effect i.e. applies across all containers/instances.

## Temporarily silencing an error

We can temporarily silence HighPercentageError alerts at [https://bots.dide.ic.ac.uk/grafana/#/silences/new](https://bots.dide.ic.ac.uk/grafana/#/silences/new). If you do this, be careful to scope the silence to the specific container and instance where the errors originate, using the filters in the UI. Note that this is a ham-fisted option since alerts cannot distinguish between different errors (log content is not available to alertmanager), and so if you silence this alert on a container/instance, we will fail to be alerted for any new class of error coming from the silenced instance during the silence.

## Permanently silencing an error

To permanently silence an error:

1. Ascertain the most specific labels to match the error (you will probably want to narrow the scope to at least the instance hostname, and the container name if applicable), and a substring of the error text for the alert logic to match against. Avoid choosing an overly generic error substring which may be caused by a different class of error.
1. Update `./config/loki/wontfix.yml` with a new entry for the labels and log matcher.
1. Run `./run --dev` to ensure that `./config/loki/alert-rules.yml` is generated as expected.
1. Pull the config change to the deployment, and reload it as per [README.md](../README.md).
