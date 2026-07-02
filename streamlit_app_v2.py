"""
Chatbot Agents BIG – Streamlit App
Dashboard multi-agents avec support PDF, Images, Vidéos
"""

import streamlit as st
import os
from pathlib import Path
import anthropic

# Configuration
st.set_page_config(
    page_title="Agents BIG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Client Anthropic
client = anthropic.Anthropic(api_key=st.secrets.get("ANTHROPIC_API_KEY"))

# Dossier documents - créer s'il n'existe pas
DOCUMENTS_DIR = Path("documents")
DOCUMENTS_DIR.mkdir(exist_ok=True)

# Extensions acceptées
ACCEPTED_EXT = {".pdf", ".jpg", ".jpeg", ".png", ".mp4", ".mov", ".avi"}

# Agents spécialisés
AGENTS = {
    "Commercial": {
        "emoji": "📞",
        "description": "Prospection, argumentaires, emails, suivi du pipeline.",
        "system": "Tu es un agent Commercial. Aide à la prospection, rédaction d'emails, suivi pipeline. Sois persuasif et orienté résultats."
    },
    "Marketing": {
        "emoji": "📣",
        "description": "Contenus, supports commerciaux, veille sectorielle, performance.",
        "system": "Tu es un agent Marketing. Aide à créer des contenus, analyser les tendances, stratégie communication. Sois créatif et data-driven."
    },
    "Juridique": {
        "emoji": "⚖️",
        "description": "Contrats, CGV, litiges, cession, RGPD.",
        "system": "Tu es un agent Juridique. Aide sur contrats, RGPD, litiges, cession. Sois précis et prudent légalement."
    },
    "Comptable / Financier": {
        "emoji": "📊",
        "description": "Analyse financière, budget, rentabilité, trésorerie.",
        "system": "Tu es un agent Comptable/Financier. Aide sur analyse financière, budget, rentabilité, trésorerie. Sois précis et chiffré."
    },
    "Administratif": {
        "emoji": "📁",
        "description": "Processus administratifs, documents, organisation.",
        "system": "Tu es un agent Administratif. Aide sur processus, gestion documentaire, organisation. Sois pragmatique et efficace."
    },
    "Technique sols industriels": {
        "emoji": "🏗️",
        "description": "Expertise technique dallage, résine, projets, reportings.",
        "system": "Tu es expert Technique sols. Aide sur dallage, résine, pilotage projets, reportings techniques. Sois expert et détaillé."
    },
    "Pilotage / Management": {
        "emoji": "🎯",
        "description": "Pilotage métier, reporting, stratégie, RH.",
        "system": "Tu es agent Pilotage/Management. Aide sur pilotage, KPIs, stratégie, management équipe. Sois visionnaire et opérationnel."
    }
}

# Session state
if "agent" not in st.session_state:
    st.session_state.agent = "Commercial"
if "messages" not in st.session_state:
    st.session_state.messages = {name: [] for name in AGENTS}

# ============= SIDEBAR =============
with st.sidebar:
    st.title("🤖 Agents BIG")
    st.markdown("### Sélectionnez un agent")
    
    for name, info in AGENTS.items():
        if st.button(f"{info['emoji']} {name}", use_container_width=True):
            st.session_state.agent = name
    
    st.divider()
    
    # Upload fichiers
    st.markdown("### 📤 Uploader fichiers")
    st.markdown("**Formats:** PDF, JPG, JPEG, PNG, MP4, MOV, AVI")
    
    uploaded = st.file_uploader(
        "Glissez/déposez vos fichiers",
        type=["pdf", "jpg", "jpeg", "png", "mp4", "mov", "avi"],
        accept_multiple_files=True
    )
    
    if uploaded:
        for file in uploaded:
            try:
                path = DOCUMENTS_DIR / file.name
                with open(path, "wb") as f:
                    f.write(file.getbuffer())
                st.success(f"✅ {file.name}")
            except Exception as e:
                st.error(f"❌ {file.name}: {e}")
    
    st.divider()
    
    # Liste fichiers
    st.markdown("### 📂 Fichiers disponibles")
    files = [f for f in DOCUMENTS_DIR.iterdir() if f.suffix.lower() in ACCEPTED_EXT]
    
    if files:
        st.markdown(f"**{len(files)} fichier(s):**")
        for f in files:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"📄 {f.name}")
            with col2:
                if st.button("🗑️", key=f.name):
                    os.remove(f)
                    st.rerun()
    else:
        st.info("Aucun fichier")

# ============= MAIN =============
agent_info = AGENTS[st.session_state.agent]

st.markdown(f"# {agent_info['emoji']} {st.session_state.agent}")
st.markdown(f"_{agent_info['description']}_")
st.divider()

# Afficher historique
for msg in st.session_state.messages[st.session_state.agent]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input chat
if prompt := st.chat_input("Posez votre question..."):
    # Ajouter message utilisateur
    st.session_state.messages[st.session_state.agent].append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Appel Claude
    with st.chat_message("assistant"):
        with st.spinner("⏳ Réflexion..."):
            try:
                response = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=2048,
                    system=agent_info["system"],
                    messages=st.session_state.messages[st.session_state.agent]
                )
                
                answer = response.content[0].text
                st.session_state.messages[st.session_state.agent].append({
                    "role": "assistant",
                    "content": answer
                })
                st.markdown(answer)
                
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

# Footer
st.divider()
st.markdown("**Agents BIG** | Bordas Industrial Group | Assistance via Claude")
