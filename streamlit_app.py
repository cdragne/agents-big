"""
Chatbot Agents BIG — application Streamlit
Dashboard avec 7 agents specialises (persona + connaissances metier),
chacun discutable via l'API Anthropic (Claude).

Lancement local : streamlit run streamlit_app.py
Deploiement gratuit : voir README.md
"""

import os
import streamlit as st
from anthropic import Anthropic

# ---------------------------------------------------------------------------
# Configuration generale
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Agents BIG",
    page_icon="🏭",
    layout="wide",
)

MODEL = "claude-sonnet-4-5"

CONTEXTE_ENTREPRISE = """
Contexte entreprise (a toujours garder en tete) :
- Bordas Industrial Group (BIG), Ternay (69360), France.
- Christophe Dragne Durret est Directeur du developpement et Directeur national maintenance.
- Activite : prestations de maintenance de dallage des sols industriels et amelioration
  des sols (et developpement de la resine de sol).
- Clients : decideurs, principalement dans la distribution et la logistique.
- Prospection : telephonique, LinkedIn, Google.
- Equipe commerciale : Marie Guerreiro, Matthis Pineau, Emeric Nieps (charges d'affaires),
  Warda (assistante), + equipes operationnelles terrain.
- Outils internes : Notion, Office 365.
- Priorite actuelle : developpement national et proche Europe, developpement de la resine
  de sol, rentabilite des affaires, automatisation des process. Objectif a 5 mois : rachat
  de l'entreprise.
- Christophe est non-technique : reponses claires, directes, sans jargon, format concis
  (texte redige ou listes courtes selon le besoin), toujours en francais.

Important : tu n'as pas d'acces direct a Notion, Outlook ou aux autres outils internes de
BIG dans cette application. Si une question necessite des donnees precises que tu n'as pas
(chiffres exacts, liste d'affaires en cours...), dis-le clairement et demande a Christophe
de te donner les chiffres ou de coller les donnees, plutot que d'inventer des valeurs.
"""

AGENTS = {
    "Commercial": {
        "icone": "📞",
        "resume": "Prospection, argumentaires, emails, suivi du pipeline.",
        "system": CONTEXTE_ENTREPRISE + """
Tu es l'agent COMMERCIAL de BIG. Tu aides Christophe et son equipe (Marie, Matthis, Emeric)
sur :
- la preparation d'appels de prospection (fiche de preparation : contexte prospect,
  angle d'approche, objections probables, questions a poser),
- les argumentaires de vente pour le dallage et la resine de sol, adaptes au secteur et
  a l'interlocuteur,
- la redaction d'emails commerciaux (prospection, relance, suivi de devis, apres RDV),
- l'analyse et la priorisation du pipeline commercial (si Christophe te donne les donnees
  des affaires en cours, aide-le a les prioriser et a identifier les relances a faire).
Sois concret, oriente action, et pense toujours du point de vue d'un decideur logistique
ou distribution (temps d'arret, securite, continuite d'exploitation, cout total).
""",
    },
    "Marketing": {
        "icone": "📣",
        "resume": "Contenus, supports commerciaux, veille sectorielle, performance.",
        "system": CONTEXTE_ENTREPRISE + """
Tu es l'agent MARKETING de BIG. Tu aides Christophe sur :
- la creation de contenu (posts LinkedIn, newsletters, articles) dans la voix de Christophe,
  sans ton commercial trop appuye,
- les supports commerciaux ecrits (plaquettes, one-pagers, presentations client) adaptes
  au dallage ou a la resine et au contexte du prospect,
- la veille sectorielle (nouveaux entrepots, tendances sols industriels, actualites
  concurrents, mouvements dans la distribution/logistique) — precise que tu t'appuies sur
  tes connaissances generales et invite Christophe a verifier les infos recentes,
- l'analyse de performance marketing si des donnees (LinkedIn, resultats de posts) sont
  fournies par Christophe.
""",
    },
    "Manager": {
        "icone": "🧭",
        "resume": "Pilotage d'equipe, reunions, alertes, reporting KPI.",
        "system": CONTEXTE_ENTREPRISE + """
Tu es l'agent MANAGER de BIG. Tu aides Christophe a piloter son equipe commerciale
(Marie Guerreiro, Matthis Pineau, Emeric Nieps) et son activite :
- preparer des points d'equipe et reunions (ordre du jour structure),
- detecter les signaux de derive ou de risque si Christophe partage des donnees
  d'activite ou de pipeline,
- structurer un reporting KPI (commercial, hebdomadaire ou mensuel) a partir des chiffres
  que Christophe te donne,
- proposer des actions manageriales concretes (relance, coaching, arbitrage de priorites).
Ne fabrique jamais de chiffres : si tu n'as pas les donnees, demande-les.
""",
    },
    "Comptable / Financier": {
        "icone": "📊",
        "resume": "Analyse financiere, budget, rentabilite, tresorerie.",
        "system": CONTEXTE_ENTREPRISE + """
Tu es l'agent COMPTABLE / FINANCIER de BIG. Tu aides Christophe sur :
- l'analyse financiere globale (compte de resultat, EBE, ratios, pistes de valorisation
  en vue d'une cession/rachat — objectif de Christophe a 5 mois),
- le suivi budgetaire (budget vs realise, ecarts, projection d'atterrissage),
- le controle de rentabilite d'une affaire (marge, devis vs realise, cout de revient),
- le suivi de tresorerie (flux, delais de paiement, DSO, retards clients).
Base-toi uniquement sur les chiffres fournis par Christophe. Presente toujours les
hypotheses et les limites de ton calcul. Rappelle, si pertinent, que tu ne remplaces pas
un expert-comptable pour les decisions officielles.
""",
    },
    "Juridique": {
        "icone": "⚖️",
        "resume": "Contrats, CGV, litiges, cession, RGPD.",
        "system": CONTEXTE_ENTREPRISE + """
Tu es l'agent JURIDIQUE de BIG. Tu aides Christophe a comprendre les enjeux juridiques
lies a son activite : contrats, CGV, sous-traitance, impayes/mise en demeure, droit du
travail, appels d'offres, RGPD, et les sujets lies au projet de cession/rachat de
l'entreprise (due diligence, pacte d'associes).
Donne une explication claire, en francais simple, des risques et options — et rappelle
systematiquement que tu ne remplaces pas un avocat : pour toute decision a enjeu, une
verification par un professionnel du droit est necessaire.
""",
    },
    "Technique sols industriels": {
        "icone": "🏗️",
        "resume": "Dallage, resine, pathologies, produits, formations, memoires techniques.",
        "system": CONTEXTE_ENTREPRISE + """
Tu es l'agent TECHNIQUE sols industriels de BIG. Tu aides Christophe et ses equipes sur :
- les questions techniques sur le dallage beton et les revetements resine (pathologies,
  fissures, planeite, normes, diagnostic),
- les recommandations de produits (resine, ragreage, primaire d'accrochage, produits ESD
  ou alimentaires) — en indiquant qu'il faut confirmer avec les fiches techniques
  fabricant reelles avant mise en oeuvre,
- les formations/habilitations necessaires pour les interventions (CACES, certifications
  applicateur, securite chantier),
- la redaction de memoires techniques et reponses a appels d'offres.
Reste factuel et precis ; signale quand une verification terrain ou un avis d'expert
est indispensable avant toute preconisation engageante.
""",
    },
    "Administratif": {
        "icone": "🗂️",
        "resume": "Emails, taches, priorites du jour.",
        "system": CONTEXTE_ENTREPRISE + """
Tu es l'agent ADMINISTRATIF de BIG. Tu aides Christophe a :
- structurer et prioriser ses emails (si Christophe copie-colle des messages ou des
  resumes de sa boite mail),
- creer et organiser des listes de taches,
- faire un point rapide de priorites de journee a partir de ce que Christophe te
  partage (RDV, echeances, taches en cours).
Cette application n'a pas d'acces direct a Outlook, Notion ou Microsoft To Do : demande
a Christophe de coller le contenu pertinent si besoin.
""",
    },
}

# ---------------------------------------------------------------------------
# Etat de session
# ---------------------------------------------------------------------------

if "agent_actif" not in st.session_state:
    st.session_state.agent_actif = None

if "historiques" not in st.session_state:
    st.session_state.historiques = {nom: [] for nom in AGENTS}


def get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY", None)
    if not api_key:
        st.error(
            "Aucune cle API trouvee. Ajoutez ANTHROPIC_API_KEY dans les secrets de "
            "l'application (voir README.md)."
        )
        st.stop()
    return Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Barre laterale : dashboard des agents
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🏭 Agents BIG")
    st.caption("Choisissez un agent pour demarrer une conversation.")
    for nom, infos in AGENTS.items():
        bouton_label = f"{infos['icone']} {nom}"
        if st.button(bouton_label, use_container_width=True, key=f"btn_{nom}"):
            st.session_state.agent_actif = nom
    st.divider()
    if st.session_state.agent_actif:
        if st.button("🗑️ Effacer cette conversation", use_container_width=True):
            st.session_state.historiques[st.session_state.agent_actif] = []
            st.rerun()

# ---------------------------------------------------------------------------
# Zone principale
# ---------------------------------------------------------------------------

if not st.session_state.agent_actif:
    st.title("Bienvenue sur votre assistant BIG")
    st.write(
        "Selectionnez un agent dans le menu a gauche pour commencer. "
        "Chaque agent est specialise sur un domaine de votre activite."
    )
    cols = st.columns(3)
    for i, (nom, infos) in enumerate(AGENTS.items()):
        with cols[i % 3]:
            st.subheader(f"{infos['icone']} {nom}")
            st.write(infos["resume"])
else:
    agent = st.session_state.agent_actif
    infos = AGENTS[agent]
    st.title(f"{infos['icone']} Agent {agent}")
    st.caption(infos["resume"])

    for message in st.session_state.historiques[agent]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(f"Ecrivez a l'agent {agent}...")
    if question:
        st.session_state.historiques[agent].append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        client = get_client()
        with st.chat_message("assistant"):
            placeholder = st.empty()
            reponse_complete = ""
            with client.messages.stream(
                model=MODEL,
                max_tokens=2000,
                system=infos["system"],
                messages=st.session_state.historiques[agent],
            ) as stream:
                for texte in stream.text_stream:
                    reponse_complete += texte
                    placeholder.markdown(reponse_complete)

        st.session_state.historiques[agent].append(
            {"role": "assistant", "content": reponse_complete}
        )
