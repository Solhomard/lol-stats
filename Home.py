import streamlit as st
import json
import pandas as pd
import os
import streamlit as st

# --- Gestion du mot de passe ---

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


# --- Configuration de la page ---

st.set_page_config(page_title="LoL Analyst", page_icon="🏆")

st.title("🏆 Accueil - Chargement des Données")

DATA_FOLDER = 'games'
ALL_MATCHES = []

def load_local_games(directory='games'):
    loaded_data = []
    if not os.path.exists(directory):
        os.makedirs(directory)
        return []

    files = os.listdir(directory)

    for filename in files:
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    loaded_data.append(data)
            except Exception as e:
                st.error(f"Erreur lors du chargement de {filename}: {e}")
    return loaded_data

if 'matches_data' not in st.session_state:
    st.session_state['matches_data'] = []

col1, col2 = st.columns(2)

with col1:
    st.subheader("Chargement Automatique")
    st.write(f"Scanne le dossier '{DATA_FOLDER}' local.")

    if st.button("Charger les matchs depuis le dossier 'games'", type='primary'):
        local_matches = load_local_games(DATA_FOLDER)
        if local_matches:
            st.session_state['matches_data'] = local_matches
            st.success(f"{len(local_matches)} parties chargées depuis le dossier local !")
        else:
            st.warning("Aucun fichier JSON trouvé dans le dossier spécifié.")

with col2:
    st.subheader("Upload Manuel")
    st.write("Uploade tes fichiers JSON de matchs.")
    uploaded_files = st.file_uploader("Glisser-déposer ici", accept_multiple_files=True, type=['json'])

    if uploaded_files:
        new_matches = []
        for file in uploaded_files:
            new_matches.append(json.load(file))
        st.session_state['matches_data'].extend(new_matches)
        st.success(f"{len(new_matches)} parties uploadées avec succès !")

st.divider()
if st.session_state['matches_data']:
    count = len(st.session_state['matches_data'])
    st.info(f"Total des parties chargées: {count}")
    with st.expander("Voir les détails des parties chargées"):
        for i, m in enumerate(st.session_state['matches_data']):
            game_id = m.get('info', {}).get('gameId', 'Inconnu')
            st.text(f"Partie {i+1}: Game ID = {game_id}")