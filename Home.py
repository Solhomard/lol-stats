import streamlit as st
import json
import pandas as pd
import os
import streamlit as st


def check_password():
    if "PASSWORD" not in st.secrets:
        return True

    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True
    
    st.text_input("Mot de passe", type="password", on_change=password_entered, key="password")

    if "password_correct" in st.session_state:
        st.error("Mot de passe incorrect")
    return False

if not check_password():
    st.stop()

st.set_page_config(page_title="LoL Analyst", page_icon="🏆")

st.title("🏆 Accueil - Chargement des Données")

DATA_FOLDER = 'games'
ALL_MATCHES = []


# 1. Widget d'upload
uploaded_files = st.file_uploader("Chargez vos JSON (Matchs + Timelines)", accept_multiple_files=True, type=['json'])

if not os.path.exists(DATA_FOLDER):
    st.error(f"Le dossier '{DATA_FOLDER}' est introuvable. Veuillez vérifier le chemin.")

if os.path.exists(DATA_FOLDER):
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.json')]

    if not files:
        st.warning("Aucun fichier JSON trouvé dans le dossier spécifié.")
    
    for filename in files:
        file_path = os.path.join(DATA_FOLDER, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                ALL_MATCHES.append(content)
        except Exception as e:
            st.error(f"Erreur lors du chargement de {filename}: {e}")
    
    st.session_state['matches_data_file'] = ALL_MATCHES
    st.success(f"{len(ALL_MATCHES)} matchs chargés depuis le dossier par défaut ! Allez voir les autres pages 👈")

# 2. Traitement et Sauvegarde en Session
if uploaded_files:
    # On vérifie si on a déjà chargé les données pour ne pas refaire le travail
    if 'matches_data' not in st.session_state:
        matches = []
        for file in uploaded_files:
            # On lit le fichier
            data = json.load(file)
            matches.append(data)
        
        # SAUVEGARDE DANS LA MÉMOIRE PARTAGÉE
        st.session_state['matches_data'] = matches
        st.success(f"{len(matches)} matchs chargés avec succès ! Allez voir les autres pages 👈")
    else:
        st.info("Données déjà chargées en mémoire.")

else:
    st.warning("Veuillez uploader des fichiers pour commencer.")