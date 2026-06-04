// Préfixe des appels API. La page est servie par nginx (HTTPS), et tous les
// appels passent par le MEME domaine sous /api : nginx les proxifie vers le
// pool de gateways. Comme c'est la même origine, plus besoin de CORS.
// Exemple : "/api/hello/users" arrive à la gateway comme "/hello/users".
const GATEWAY = "/api";


// Fonction utilitaire : appelle un endpoint GET et affiche la réponse.
async function callApi(path, outputId) {
  const out = document.getElementById(outputId);
  out.textContent = "Chargement...";
  try {
    const r = await fetch(GATEWAY + path);
    const data = await r.json();
    out.textContent = "Code " + r.status + " :\n" + JSON.stringify(data, null, 2);
  } catch (err) {
    out.textContent = "Erreur : " + err.message;
  }
}


// Crée un utilisateur via POST /hello/users avec un corps JSON.
async function createUser() {
  const name = document.getElementById("user-name").value;
  const out = document.getElementById("create-out");
  if (!name) {
    out.textContent = "Le nom est obligatoire.";
    return;
  }
  out.textContent = "Chargement...";
  try {
    const r = await fetch(GATEWAY + "/hello/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name }),
    });
    const data = await r.json();
    out.textContent = "Code " + r.status + " :\n" + JSON.stringify(data, null, 2);
  } catch (err) {
    out.textContent = "Erreur : " + err.message;
  }
}


// Récupère un utilisateur par son id.
function getUser() {
  const id = document.getElementById("user-id").value;
  if (!id) {
    document.getElementById("get-out").textContent = "L'ID est obligatoire.";
    return;
  }
  callApi("/hello/users/" + id, "get-out");
}


// Démo du LOAD BALANCING (séance 8).
// On appelle /api/whoami six fois. nginx répartit chaque appel sur l'une des
// trois instances de la gateway, donc le nom d'hôte renvoyé change : on voit
// le round-robin en direct.
async function whoAmI() {
  const out = document.getElementById("lb-out");
  out.textContent = "Chargement...";
  const lignes = [];
  for (let i = 1; i <= 6; i++) {
    try {
      const r = await fetch(GATEWAY + "/whoami");
      const data = await r.json();
      lignes.push("Appel " + i + " : gateway " + data.gateway_host);
    } catch (err) {
      lignes.push("Appel " + i + " : erreur " + err.message);
    }
  }
  out.textContent = lignes.join("\n");
}
