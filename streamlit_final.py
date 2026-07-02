#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import os
from pathlib import Path

# Configuration page
st.set_page_config(
    page_title="Agents BIG",
    page_icon="🤖",
    layout="wide"
)

# Test API
try:
    from anthropic import Anthropic
    api_key = st.secrets.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY manquante")
        st.stop()
    client = Anthropic(api_key=api_key)
except ImportError:
    st.error("❌ anthropic non installé")
    st.stop()
except Exception as e:
    st.error(f"❌ Erreur: {e}")
    st.stop()

# Dossier documents
DOCS = Path("documents")
DOCS.mkdir(exist_ok=True)

# Agents
AGENTS = {
    "Commercial": "Vous êtes un agent Commercial expert. Aidez à la prospection, rédaction emails, suivi pipeline.",
    "Marketing": "Vous êtes un agent Marketing. Aidez à créer contenus et analyser tendances.",
    "Juridique": "Vous êtes un agent Juridique. Aidez sur contrats, RGPD, litiges.",
    "Comptable": "Vous êtes un expert Comptable/Financier. Aidez sur analyses financières, budget.",
    "Administratif": "Vous êtes un agent Administratif. Aidez sur processus, documentation.",
    "Technique sol": "Vous êtes expert Technique sols industriels. Aidez sur dallage, résine, projets.",
    "Management": "Vous êtes un agent Management. Aidez sur stratégie et reporting."
}

# State
if "agent" not in st.session_state:
    st.session_state.agent = "Commercial"
if "messages" not in st.session_state:
    st.session_state.messages = {a: [] for a in AGENTS}

# === SIDEBAR ===
with st.sidebar:
    st.title("🤖 Agents BIG")
    st.markdown("**Sélectionnez un agent**")
    
    col1, col2 = st.columns(2)
    for idx, agent_name in enumerate(list(AGENTS.keys())):
        with col1 if idx % 2 == 0 else col2:
            if st.button(agent_name, use_container_width=True, key=f"agent_{agent_name}"):
                st.session_state.agent = agent_name
    
    st.divider()
    st.markdown("**📤 Ajouter fichiers**")
    
    uploaded = st.file_uploader(
        "PDF, JPG, PNG, MP4, MOV",
        type=["pdf", "jpg", "jpeg", "png", "mp4", "mov", "avi"],
        accept_multiple_files=True
    )
    
    if uploaded:
        for file in uploaded:
            try:
                path = DOCS / file.name
                with open(path, "wb") as f:
                    f.write(file.getbuffer())
                st.success(f"✅ {file.name}")
            except Exception as e:
                st.error(f"❌ {str(e)[:50]}")
    
    st.divider()
    st.markdown("**📂 Fichiers disponibles**")
    
    files = list(DOCS.glob("*"))
    if files:
        st.markdown(f"**{len(files)} fichier(s)**")
        for f in files:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"📄 {f.name}")
            with col2:
                if st.button("🗑️", key=f.name, help="Supprimer"):
                    try:
                        os.remove(f)
                        st.rerun()
                    except:
                        st.error("Erreur")
    else:
        st.info("Aucun fichier")

# === MAIN ===
st.markdown(f"# {st.session_state.agent}")
st.divider()

# Chat history
for msg in st.session_state.messages[st.session_state.agent]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Posez votre question..."):
    # Add user message
    st.session_state.messages[st.session_state.agent].append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Call Claude
    with st.chat_message("assistant"):
        with st.spinner("Réflexion..."):
            try:
                response = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=1024,
                    system=AGENTS[st.session_state.agent],
                    messages=st.session_state.messages[st.session_state.agent]
                )
                
                answer = response.content[0].text
                st.session_state.messages[st.session_state.agent].append({
                    "role": "assistant",
                    "content": answer
                })
                st.markdown(answer)
                
            except Exception as e:
                st.error(f"❌ Erreur API: {str(e)[:100]}")

st.divider()
st.caption("Agents BIG | Bordas Industrial Group")
