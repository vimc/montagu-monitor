#!/usr/bin/env bash
set -e
here=$(dirname $0)

$here/configure/configure.py > aws_configuration
tmp=$(docker run -dt --rm -v aws_metrics_config:/data alpine)
docker cp aws_configuration $tmp:/data/credentials
docker kill $tmp
rm aws_configuration
