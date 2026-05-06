// URL du gateway. Tous les appels passent par le port 8000.
// Si tu changes GATEWAY_PORT dans .env, change aussi cette ligne.
const GATEWAY = "http://localhost:8000";


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
