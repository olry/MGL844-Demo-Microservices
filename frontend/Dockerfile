# Image de base : nginx en version légère (alpine).
# nginx sert juste les fichiers statiques HTML/CSS/JS.
FROM nginx:alpine

# On installe envsubst (paquet gettext) pour générer config.js au démarrage
# à partir de config.template.js et de la variable GATEWAY_PORT.
RUN apk add --no-cache gettext

# On copie les fichiers du frontend dans le dossier que nginx sert
# par défaut.
COPY index.html style.css app.js config.template.js /usr/share/nginx/html/

# Script d'entree qui genere config.js avant que nginx ne demarre.
# nginx-alpine lance automatiquement les scripts de /docker-entrypoint.d/.
COPY docker-entrypoint.sh /docker-entrypoint.d/40-config.sh
RUN chmod +x /docker-entrypoint.d/40-config.sh

# Port exposé par le conteneur (nginx écoute sur 80 à l'intérieur).
EXPOSE 80
