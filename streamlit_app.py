"""
Chatbot Agents BIG – application Streamlit
Dashboard avec 7 agents specialises (persona + connaissances metier)
chacun discutable via l'API Anthropic (Claude).

Support: PDF, Images (JPG, JPEG, PNG), Vidéos (MP4, MOV, AVI)
"""

import streamlit as st
import os
from pathlib import Path
import anthropic

# Configuration Streamlit
st.set_page_config(
    page_title="Chatbot Agents BIG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialiser le client Anthropic
client = anthropic.Anthropic(api_key=st.secrets.get("ANTHROPIC_API_KEY"))

# ========================
# CONFIGURATION DES FICHIERS
# ========================

DOCUMENTS_DIR = Path("documents")
MODELS_DIR = Path("models")

# Extensions acceptées
ACCEPTED_EXTENSIONS = {
    # Documents
    ".pdf",
    # Images
    ".jpg", ".jpeg", ".png",
    # Vidéos
    ".mp4", ".mov", ".avi"
}

def get_all_files():
    """Récupérer tous les fichiers acceptés des dossiers documents et models"""
    files = []
    
    # Chercher dans documents/
    if DOCUMENTS_DIR.exists():
        for file in DOCUMENTS_DIR.iterdir():
            if file.is_file() and file.suffix.lower() in ACCEPTED_EXTENSIONS:
                files.append({
                    'name': file.name,
                    'path': str(file),
                    'type': get_file_type(file.suffix.lower())
                })
    
    # Chercher dans models/
    if MODELS_DIR.exists():
        for file in MODELS_DIR.iterdir():
            if file.is_file() and file.suffix.lower() in ACCEPTED_EXTENSIONS:
                files.append({
                    'name': file.name,
                    'path': str(file),
                    'type': get_file_type(file.suffix.lower())
                })
    
    return sorted(files, key=lambda x: x['name'])

def get_file_type(extension):
    """Déterminer le type de fichier"""
    if extension == ".pdf":
        return "PDF"
    elif extension in [".jpg", ".jpeg", ".png"]:
        return "Image"
    elif extension in [".mp4", ".mov", ".avi"]:
        return "Vidéo"
    return "Fichier"

# ========================
# AGENTS SPECIALISES
# ========================

AGENTS = {
    "Commercial": {
        "emoji": "📞",
        "color": "#FF6B6B",
        "description": "Prospection, argumentaires, emails, suivi du pipeline.",
        "system_prompt": """Tu es un agent Commercial expert. Tu aides à:
- Prospection et argumentaires de vente
- Rédaction d'emails commerciaux
- Suivi du pipeline
- Stratégie tarifaire
Sois persuasif, clair et orienté résultats."""
    },
    "Marketing": {
        "emoji": "📣",
        "color": "#FFA500",
        "description": "Contenus, supports commerciaux, veille sectorielle, performance.",
        "system_prompt": """Tu es un agent Marketing expert. Tu aides à:
- Création de contenus et supports commerciaux
- Veille sectorielle et tendances
- Analyse de performance
- Stratégie de communication
Sois créatif et data-driven."""
    },
    "Juridique": {
        "emoji": "⚖️",
        "color": "#4169E1",
        "description": "Contrats, CGV, litiges, cession, RGPD.",
        "system_prompt": """Tu es un agent Juridique expert. Tu aides à:
- Rédaction et analyse de contrats
- Questions RGPD et conformité
- Gestion des litiges
- Cession et restructuration
Sois précis et prudent légalement."""
    },
    "Comptable / Financier": {
        "emoji": "📊",
        "color": "#28A745",
        "description": "Analyse financière, budget, rentabilité, trésorerie.",
        "system_prompt": """Tu es un agent Comptable/Financier expert. Tu aides à:
- Analyse financière et budget
- Rentabilité des affaires
- Gestion de trésorerie
- Reporting financier
Sois précis et chiffré."""
    },
    "Administratif": {
        "emoji": "📁",
        "color": "#FFC107",
        "description": "Processus administratifs, documents, organisation.",
        "system_prompt": """Tu es un agent Administratif expert. Tu aides à:
- Optimisation des processus administratifs
- Gestion documentaire
- Organisation interne
- Conformité administrative
Sois pragmatique et efficace."""
    },
    "Technique sols industriels": {
        "emoji": "🏗️",
        "color": "#20C997",
        "description": "Pilotage projets, reportings, expertise technique sol.",
        "system_prompt": """Tu es un expert Technique en sols industriels. Tu aides à:
- Expertise technique dallage et résine
- Pilotage de projets
- Reportings techniques
- Solutions de rénovation sol
Sois expert et détaillé."""
    },
    "Pilotage / Management": {
        "emoji": "🎯",
        "color": "#6F42C1",
        "description": "Pilotage métier, reporting, stratégie, RH.",
        "system_prompt": """Tu es un agent Pilotage/Management expert. Tu aides à:
- Pilotage du développement
- KPIs et reporting
- Stratégie métier
- Management d'équipe
Sois visionnaire et opérationnel."""
    }
}

# ========================
# SESSION STATE
# ========================

if "current_agent" not in st.session_state:
    st.session_state.current_agent = "Commercial"

if "messages" not in st.session_state:
    st.session_state.messages = {}

# Initialiser historique pour chaque agent
for agent_name in AGENTS:
    if agent_name not in st.session_state.messages:
        st.session_state.messages[agent_name] = []

# ========================
# UI - SIDEBAR
# ========================

with st.sidebar:
    st.title("🤖 Agents BIG")
    
    st.markdown("### Sélectionnez un agent")
    for agent_name, agent_info in AGENTS.items():
        btn_color = agent_info["color"]
        if st.button(
            f"{agent_info['emoji']} {agent_name}",
            key=f"btn_{agent_name}",
            use_container_width=True,
            help=agent_info["description"]
        ):
            st.session_state.current_agent = agent_name
    
    st.divider()
    
    # Section documents
    st.markdown("### 📂 Documents / Média")
    files = get_all_files()
    
    if files:
        st.markdown(f"**{len(files)} fichier(s) disponible(s):**")
        for file in files:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"📄 {file['name']}")
            with col2:
                st.caption(f"({file['type']})")
    else:
        st.warning("❌ Aucun fichier détecté")
        st.info("""Mettez des fichiers dans:
- `/documents/`
- `/models/`

Formats acceptés:
- PDFs
- Images: JPG, JPEG, PNG
- Vidéos: MP4, MOV, AVI
        """)

# ========================
# UI - MAIN
# ========================

agent = AGENTS[st.session_state.current_agent]

st.markdown(f"# {agent['emoji']} {st.session_state.current_agent}")
st.markdown(f"_{agent['description']}_")
st.divider()

# Afficher l'historique de conversation
messages_history = st.session_state.messages[st.session_state.current_agent]

for msg in messages_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ========================
# INPUT - CHAT
# ========================

if prompt := st.chat_input("Posez votre question..."):
    # Ajouter le message utilisateur
    st.session_state.messages[st.session_state.current_agent].append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Appel API Claude
    with st.chat_message("assistant"):
        with st.spinner("⏳ Réflexion en cours..."):
            try:
                response = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=2048,
                    system=agent["system_prompt"],
                    messages=st.session_state.messages[st.session_state.current_agent]
                )
                
                assistant_message = response.content[0].text
                
                # Ajouter la réponse à l'historique
                st.session_state.messages[st.session_state.current_agent].append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                st.markdown(assistant_message)
                
            except Exception as e:
                st.error(f"❌ Erreur API: {str(e)}")

# ========================
# FOOTER
# ========================

st.divider()
st.markdown("""
---
**Chatbot Agents BIG** | Bordas Industrial Group
Assistance décisionnelle multifonctions via Claude
""")
