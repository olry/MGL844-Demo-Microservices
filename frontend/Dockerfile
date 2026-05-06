# Image de base : nginx en version légère (alpine).
# nginx sert juste les fichiers statiques HTML/CSS/JS.
FROM nginx:alpine

# On copie les trois fichiers du frontend dans le dossier que nginx sert
# par défaut.
COPY index.html style.css app.js /usr/share/nginx/html/

# Port exposé par le conteneur (nginx écoute sur 80 à l'intérieur).
EXPOSE 80
