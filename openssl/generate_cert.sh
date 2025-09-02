#!/bin/sh
set -e

openssl req -x509 \
   -newkey rsa:2048 \
   -nodes \
   -keyout /tls/key.pem \
   -out /tls/certificate.pem \
   -days 365 \
   -subj "/C=GB/ST=GB/L=London/O=Imperial College/OU=Reside/CN=localhost"
