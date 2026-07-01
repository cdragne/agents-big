# Chatbot Agents BIG

Application web avec un tableau de bord de 7 agents specialises (commercial, marketing,
manager, comptable, juridique, technique, administratif), chacun discutable dans une
fenetre de chat.

Hebergement gratuit via **Streamlit Community Cloud**. Cout reel : uniquement l'usage de
votre cle API Anthropic (facturee a la consommation, quelques centimes par echange).

## Deploiement (10 minutes, sans ligne de commande)

### 1. Mettre les fichiers sur GitHub
1. Creez un compte gratuit sur [github.com](https://github.com) si vous n'en avez pas.
2. Cliquez sur "New repository", nommez-le par exemple `agents-big`, laissez-le "Public"
   ou "Private" (peu importe), puis "Create repository".
3. Sur la page du repository, cliquez sur "uploading an existing file" et glissez les
   3 fichiers de ce dossier (`streamlit_app.py`, `requirements.txt`, `README.md`).
4. Cliquez sur "Commit changes".

### 2. Deployer sur Streamlit Community Cloud
1. Allez sur [share.streamlit.io](https://share.streamlit.io) et connectez-vous avec
   votre compte GitHub.
2. Cliquez sur "New app".
3. Choisissez le repository `agents-big`, la branche `main`, et le fichier
   `streamlit_app.py`.
4. Avant de cliquer sur "Deploy", ouvrez "Advanced settings" > "Secrets" et collez :

   ```
   ANTHROPIC_API_KEY = "votre-cle-api-ici"
   ```

5. Cliquez sur "Deploy". Au bout de 1 a 2 minutes, votre application est en ligne avec
   une adresse du type `https://agents-big-xxxx.streamlit.app`.

C'est cette adresse que vous pouvez garder en favori et ouvrir depuis n'importe quel
navigateur (ordinateur, tablette, telephone).

## Limites de cette version

- L'application **n'a pas acces** a vos donnees Notion, Outlook ou Microsoft 365 : les
  agents repondent avec leurs connaissances metier, mais ne lisent pas vos fichiers ou
  votre boite mail. Si un agent a besoin de chiffres precis, collez-les directement dans
  le chat.
- Chaque agent a sa propre memoire de conversation, remise a zero si vous rechargez la
  page (bouton "Effacer cette conversation" pour repartir a zero volontairement).
- Une seule personne a la fois est prevue pour cette version (pas de comptes utilisateurs
  separes). Si vous voulez ouvrir l'acces a votre equipe plus tard, on pourra ajouter
  une protection par mot de passe.

## Modifier le comportement d'un agent

Tout le contenu de chaque agent (ce qu'il sait, comment il repond) est dans le fichier
`streamlit_app.py`, dans le dictionnaire `AGENTS`, champ `"system"`. Vous pouvez me
redonner ce fichier a modifier si vous voulez ajuster le ton ou les connaissances d'un
agent.
