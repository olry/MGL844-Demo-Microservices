# ============================================================================
#  Genere un certificat TLS auto-signe pour le labo (CN=localhost), sous Windows.
#  A lancer une seule fois ; le certificat est valable 825 jours.
#
#  ATTENTION : certificat de DEMO uniquement. Le navigateur affichera un
#  avertissement de securite (certificat non signe par une autorite) : c'est
#  normal en labo, on clique "continuer". En production, on utilise
#  Let's Encrypt (certbot) pour des certificats reconnus et renouveles.
# ============================================================================
$ErrorActionPreference = "Stop"
$root  = Split-Path -Parent $PSScriptRoot
$certs = Join-Path $root "nginx\certs"
New-Item -ItemType Directory -Force -Path $certs | Out-Null

# On genere via un conteneur pour ne dependre d'aucun openssl installe en local.
docker run --rm -v "${certs}:/certs" alpine/openssl `
  req -x509 -newkey rsa:2048 -nodes -days 825 `
  -keyout /certs/server.key -out /certs/server.crt `
  -subj "/CN=localhost"

Write-Host "Certificat genere dans nginx/certs/ (server.crt + server.key)."
