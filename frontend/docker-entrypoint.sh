#!/bin/sh
# Script lancé au démarrage du conteneur, AVANT nginx.
# Il remplace ${GATEWAY_PORT} dans config.template.js par la vraie valeur
# venant du .env, et écrit le résultat dans config.js (servi par nginx).
set -e

if [ -z "$GATEWAY_PORT" ]; then
  echo "ERREUR : la variable GATEWAY_PORT n'est pas definie." >&2
  exit 1
fi

envsubst '${GATEWAY_PORT}' \
  < /usr/share/nginx/html/config.template.js \
  > /usr/share/nginx/html/config.js
