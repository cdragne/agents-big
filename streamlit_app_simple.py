import streamlit as st
import os
from pathlib import Path
import anthropic

# Configuration
st.set_page_config(page_title="Agents BIG", page_icon="🤖", layout="wide")

# Client Anthropic
try:
    api_key = st.secrets.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("❌ Clé API manquante. Configurez ANTHROPIC_API_KEY dans les secrets.")
        st.stop()
    client = anthropic.Anthropic(api_key=api_key)
except Exception as e:
    st.error(f"❌ Erreur initialisation: {str(e)}")
    st.stop()

# Dossier documents
DOCUMENTS_DIR = Path("documents")
DOCUMENTS_DIR.mkdir(exist_ok=True)

# Extensions acceptées
ACCEPTED_EXT = {".pdf", ".jpg", ".jpeg", ".png", ".mp4", ".mov", ".avi"}

# Agents
AGENTS = {
    "Commercial": "Tu es un agent Commercial. Aide à la prospection, rédaction d'emails, suivi pipeline.",
    "Marketing": "Tu es un agent Marketing. Aide à créer des contenus et analyser les tendances.",
    "Juridique": "Tu es un agent Juridique. Aide sur contrats, RGPD, litiges.",
    "Comptable / Financier": "Tu es un agent Comptable/Financier. Aide sur analyses financières et budget.",
    "Administratif": "Tu es un agent Administratif. Aide sur processus et gestion documentaire.",
    "Technique sols industriels": "Tu es expert Technique sols. Aide sur dallage, résine, projets.",
    "Pilotage / Management": "Tu es agent Pilotage/Management. Aide sur stratégie et reporting."
}

# Session state
if "agent" not in st.session_state:
    st.session_state.agent = "Commercial"
if "messages" not in st.session_state:
    st.session_state.messages = {name: [] for name in AGENTS}

# SIDEBAR
with st.sidebar:
    st.title("🤖 Agents BIG")
    
    # Sélection agent
    selected = st.radio("Sélectionnez un agent:", list(AGENTS.keys()), key="agent_select")
    st.session_state.agent = selected
    
    st.divider()
    
    # Upload
    st.markdown("### 📤 Ajouter fichiers")
    uploaded = st.file_uploader(
        "PDF, Images (JPG/PNG), Vidéos (MP4/MOV/AVI)",
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
                st.error(f"❌ {file.name}")
    
    st.divider()
    
    # Liste fichiers
    st.markdown("### 📂 Fichiers")
    files = [f for f in DOCUMENTS_DIR.iterdir() if f.suffix.lower() in ACCEPTED_EXT]
    
    if files:
        st.markdown(f"**{len(files)} fichier(s):**")
        for f in files:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.caption(f"📄 {f.name}")
            with col2:
                if st.button("🗑️", key=f.name):
                    os.remove(f)
                    st.rerun()
    else:
        st.info("Aucun fichier")

# MAIN
st.markdown(f"# {st.session_state.agent}")
st.divider()

# Chat historique
for msg in st.session_state.messages[st.session_state.agent]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Posez votre question..."):
    st.session_state.messages[st.session_state.agent].append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("⏳ Réflexion..."):
            try:
                response = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=2048,
                    system=AGENTS[st.session_state.agent],
                    messages=st.session_state.messages[st.session_state.agent]
                )
                
                answer = response.content[0].text
                st.session_state.messages[st.session_state.agent].append({"role": "assistant", "content": answer})
                st.markdown(answer)
                
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

st.divider()
st.caption("Agents BIG | Bordas Industrial Group")
