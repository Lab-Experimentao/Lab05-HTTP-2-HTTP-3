#!/bin/bash
# Faz o Chrome confiar na CA local do Caddy e mantém o container vivo.
set -e
CA=/caddy/caddy/pki/authorities/local/root.crt
DB=/root/.pki/nssdb

until [ -s "$CA" ]; do sleep 1; done
rm -rf "$DB"
mkdir -p "$DB"
certutil -d "sql:$DB" -N --empty-password
certutil -d "sql:$DB" -A -t C,, -n caddy -i "$CA"

exec sleep infinity
