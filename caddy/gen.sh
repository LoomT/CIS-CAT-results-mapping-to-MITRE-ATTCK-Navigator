#!/usr/bin/env bash

# Generate private key
openssl genrsa -out ./certs/private.key 2048

# Generate certificate signing request (CSR)
openssl req -new -key ./certs/private.key -out ./certs/cert.csr \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=cis-cat.local"

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in ./certs/cert.csr \
  -signkey ./certs/private.key -out ./certs/cert.crt

# Create a certificate that works for multiple domains
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ./certs/private.key \
  -out ./certs/cert.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=cis-cat.local" \
  -addext "subjectAltName=DNS:localhost,DNS:cis-cat.local,IP:127.0.0.1"