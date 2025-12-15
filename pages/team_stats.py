import streamlit as st
import json
import pandas as pd
import plotly.express as px
import os

# --- Configuration de la page ---

DATA_FOLDER = 'games'
TARGET_PLAYERS = ["Magical craft", "Frozabys", "LeDoréLoup", "KatastrOhfiak", "Ohfiak"]
ROLE_ORDER = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]


st.set_page_config(page_title="Clash Analyst", layout="wide")

st.title("⚔️ Analyseur de Stats League of Legends")
st.markdown("Uploade tes fichiers JSON pour visualiser les performances.")

# --- 1. Zone d'upload (Sidebar) ---
st.sidebar.header("Données")
uploaded_files = st.sidebar.file_uploader(
    "Charge tes fichiers JSON de match", 
    type=['json'], 
    accept_multiple_files=True
)

@st.cache_data
def load_data(folder_path):
    all_matches = []
    
    if not os.path.exists(folder_path):
        st.error(f"Le dossier '{folder_path}' est introuvable.")
        return []
    
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

    if not files:
        st.warning("Aucun fichier JSON trouvé dans le dossier.")
        return []
    
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                all_matches.append(content)
        except Exception as e:
            st.error(f"Erreur lors du chargement de {filename}: {e}")
    return all_matches


# --- 2. Fonction de traitement des données ---
def process_files(matches):
    data_rows = []
    all_found_players = set()
    
    for i, match in enumerate(matches):
        # Streamlit gère les fichiers comme des objets bytes, il faut les lire
        #matches.seek(0)
        #content = json.load(matches)
        game_label = f"Game {i+1}"
        
        if 'info' in match: 
            participants = match['info']['participants']

            for player in participants:
                name = player.get('riotIdGameName')

                if name:
                    all_found_players.add(name)

                if name in TARGET_PLAYERS:
                    # On récupère toutes les stats intéressantes d'un coup
                    row = {
                        "Game": game_label,
                        "Joueur": name,
                        "Champion": player['championName'],
                        "Position_Raw": player.get('teamPosition', 'UNKNOWN'),
                        "Dégâts": player['totalDamageDealtToChampions'],
                        "Dégâts (%)": player.get('challenges', {}).get('teamDamagePercentage', 0),
                        "Gold": player['goldEarned'],
                        "KDA": f"{player['kills']}/{player['deaths']}/{player['assists']}"
                    }
                    data_rows.append(row)
                    
    
    df = pd.DataFrame(data_rows)

    if not df.empty:
        # Nettoyage et ordonnancement des positions
        df['Position_Raw'] = pd.Categorical(df['Position_Raw'], categories=ROLE_ORDER, ordered=True)
        df = df.sort_values(by=['Game', 'Position_Raw'])

    return df, list(all_found_players)

matches_data = load_data(DATA_FOLDER)

# --- 3. Affichage Principal ---
if matches_data:
    st.success(f"✅ {len(matches_data)} parties chargées depuis le serveur.")
    # Création du DataFrame (Tableau de données)
    df, all_players_list = process_files(matches_data)
    
    if df.empty:
        st.error("Aucun des joueurs ciblés n'a été trouvé dans les fichiers uploadés.")
        st.write("Joueurs trouvés : " + ", ".join(all_players_list))


    else:
            
        # Sélecteur de stat
        stat_choice = st.radio(
            "Quelle statistique afficher ?",
            ["Dégâts", "Dégâts (%)", "Gold"],
            horizontal=True
        )
        
        # Création du graphique interactif avec PLOTLY
        if stat_choice == "Dégâts":
            y_axis = "Dégâts"
            title = "Dégâts totaux par partie"
            text_format = "%{y:.2s}" # Format compact (25k)
        elif stat_choice == "Dégâts (%)":
            y_axis = "Dégâts (%)"
            title = "Pourcentage des dégâts de l'équipe"
            text_format = "%{y:.1%}" # Format pourcentage
        else:
            y_axis = "Gold"
            title = "Or gagné"
            text_format = "%{y}"

        # Construction du graphique
        fig = px.bar(
            df, 
            x="Joueur", 
            y=y_axis, 
            color="Game", 
            text="Champion", # Affiche le nom du champion dans la barre
            title=title,
            hover_data=["KDA", "Champion"], # Ce qui apparait quand on passe la souris
            barmode="stack"
        )
    
        # Personnalisation du texte
        fig.update_traces(texttemplate='%{text}<br>' + text_format, textposition='inside')
        fig.update_layout(height=600)

        # Affichage sur le site
        st.plotly_chart(fig, use_container_width=True)
    
        # Afficher le tableau de données brut en dessous si on veut vérifier
        with st.expander("Voir les données brutes"):
            st.dataframe(df)

else:
    st.info("👈 En attente de fichiers JSON dans la barre latérale.")