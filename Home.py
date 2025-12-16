import streamlit as st
import json
import pandas as pd
import os
import streamlit as st
import requests
import time

# --- Gestion du mot de passe ---

#def check_password():
#    if "PASSWORD" not in st.secrets:
#        return True
#
#    def password_entered():
#        if st.session_state["password"] == st.secrets["PASSWORD"]:
#            st.session_state["password_correct"] = True
#            del st.session_state["password"]
#        else:
#            st.session_state["password_correct"] = False
#
#    if st.session_state.get("password_correct", False):
#        return True
#    
#    st.text_input("Mot de passe", type="password", on_change=password_entered, key="password")
#
#    if "password_correct" in st.session_state:
#        st.error("Mot de passe incorrect")
#    return False
#
#if not check_password():
#    st.stop()


# --- Configuration de la page ---

st.set_page_config(page_title="LoL Analyst", page_icon="🏆", layout="wide")

st.title("🏆 Accueil - Chargement des Données")

if "RIOT_API_KEY" in st.secrets:
    DEFAULT_KEY = st.secrets["RIOT_API_KEY"]
else:
    DEFAULT_KEY = ""
DATA_FOLDER = 'games'
ALL_MATCHES = []

if 'matches_data' not in st.session_state:
    st.session_state['matches_data'] = []

def get_puuid(game_name, tag_line, region="europe", api_key=None):
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("puuid")
    else:
        st.error(f"Erreur lors de la récupération du PUUID pour {game_name} : {response.status_code}")
        return None
    
def get_match_ids(puuid, region="europe", api_key=None, count=5):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erreur lors de la récupération des Match IDs pour PUUID {puuid} : {response.status_code}")
        return []
    
def get_match_details(match_id, region="europe", api_key=None):
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erreur lors de la récupération des détails du match {match_id} : {response.status_code}")
        return None

# -- Fonction de chargement des fichiers locaux --

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


# --- Récupération des données via l'API Riot ---

with st.container():
    st.subheader("Récupère les données directement depuis l'API Riot")

    col1, col2, col3 = st.columns(3)
    with col1:
        riot_id = st.text_input("Game Name", value="LeDoréLoup")
    with col2:
        tag_line = st.text_input("Tag Line (ex: EUW)", value="EUW")
    with col3:
        nb_games = st.slider("Nombre de parties à récupérer", min_value=1, max_value=10, value=5)

    if st.button("Lancer la recherche", type="primary"):
        if not DEFAULT_KEY:
            st.error("clé API Riot non valide.")
        else:
            status_text = st.empty()
            progress_bar = st.progress(0)

            try:
                status_text.text(f"Recherche du joueur {riot_id}#{tag_line}...")
                puuid = get_puuid(riot_id, tag_line, api_key=DEFAULT_KEY)

                if not puuid:
                    status_text.text("Joueur non trouvé. Vérifiez le Game Name et le Tag Line.")
                else:
                    status_text.text("Récupération de l'historique des matchs...")
                    progress_bar.progress(20)
                    match_ids = get_match_ids(puuid, api_key=DEFAULT_KEY, count=nb_games)

                    if not match_ids:
                        status_text.text("Aucun match trouvé pour ce joueur.")
                    else:
                        downloaded_matches = []
                        for i, match_id in enumerate(match_ids):
                            status_text.text(f"Téléchagement de la partie {i+1}")
                            match_data = get_match_details(match_id, api_key=DEFAULT_KEY)

                            if match_data:
                                downloaded_matches.append(match_data)
                            
                            progress_bar.progress(20 + int(80 * (i + 1) / len(match_ids)))
                            time.sleep(0.2) 
                        
                        st.session_state['matches_data'].extend(downloaded_matches)
                        st.text("Terminé !")
                        st.success(f"{len(downloaded_matches)} parties téléchargées et ajoutées aux données existantes.")
                        st.balloons()
            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")

st.divider()
if st.session_state['matches_data']:
    st.info(f"Mémoire Actuelle : {len(st.session_state['matches_data'])} parties chargées.")

    if st.button("Effacer les données chargées", type="secondary"):
        st.session_state['matches_data'] = []
        st.rerun()
else:
    st.warning("Aucune donnée en mémoire.")