# AWS metrics exporters

So far, this is a small Flask app that monitors statically configured S3
buckets. We could extend it to also monitor other AWS services, but first check
[what's already available for Prometheus](https://prometheus.io/docs/instrumenting/exporters/).

To run this separately from the whole monitoring solution, use the `run` script
in this directory. This will still run it in a docker container.
