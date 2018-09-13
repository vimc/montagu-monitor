#!/usr/bin/env bash
set -ex
here=$(dirname $0)

docker volume rm aws_metrics_config || echo "No volume to remove"
$here/configure/configure.py > aws_configuration
tmp=$(docker run -dt --rm -v aws_metrics_config:/data alpine)
docker cp aws_configuration $tmp:/data/credentials
docker kill $tmp
rm aws_configuration
