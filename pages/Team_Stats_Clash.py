import streamlit as st
import json
import pandas as pd
import plotly.express as px
import os
        #"KDA": {"col": "KDA_Ratio", "title": "Ration KDA", "fmt": "%{y:.2f}"},

STATS_CONFIG = {
    "Combat": {
        "Kills": {"col": "Kills", "title": "Kills par partie", "fmt": "%{y}"},
        "Dégâts": {"col": "Dégâts", "title": "Dégâts aux champions", "fmt": "%{y:.2s}"},
        "Dégâts (%)": {"col": "Dégâts (%)", "title": "Part des dégâts de l'équipe", "fmt": "%{y:.1%}"},
        "Kill Participation": {"col": "Kill Participation", "title": "Participation aux Kills (%)", "fmt": "%{y:.1%}"},
        "Dégâts Objectifs": {"col": "Dégâts Objectifs", "title": "Dégâts aux Objectifs (Tours/Dragons...)", "fmt": "%{y:.2s}"},
    },
    "Tanking": {
        "Dégâts Reçus": {"col": "Dégâts Reçus", "title": "Dégâts Reçus", "fmt": "%{y:.2s}"},
        "Dégâts Réduits": {"col": "Dégâts Réduits sur soi", "title": "Dégâts auto-mitigés", "fmt": "%{y:.2s}"},
    },
    "Farming & Gold": {
        "CS/Min": {"col": "Nombre de CS par minute", "title": "Farm par minute", "fmt": "%{y:.1f}"},
        "CS @10": {"col": "Nombre de CS at 10", "title": "CS à 10 minutes", "fmt": "%{y}"},
        "Gold": {"col": "Gold", "title": "Or gagné", "fmt": "%{y:.2s}"},
    },
    "Vision": {
        "Score Vision": {"col": "Score de Vision", "title": "Score de Vision", "fmt": "%{y}"},
        "Wards Posées": {"col": "Wards Placed", "title": "Balises posées", "fmt": "%{y}"},
    }
}

# --- Configuration de la page ---

TARGET_PLAYERS = ["Magical craft", "Frozabys", "LeDoréLoup", "KatastrOhfiak", "Ohfiak"]
ROLE_ORDER = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
matches_data = []

st.set_page_config(page_title="Clash Analyst", layout="wide")
st.title("⚔️ Analyseur de Stats League of Legends")

if 'matches_data' not in st.session_state or not st.session_state['matches_data']:
    st.error("Données manquantes. Allez à l'Accueil.")
else:
    matches_data = st.session_state['matches_data']


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
                    row = {
                        "Game": game_label,
                        "Joueur": name,
                        "Champion": player['championName'],
                        "Position_Raw": player.get('teamPosition', 'UNKNOWN'),

                        # Stats Combat
                        "Kills": player['kills'],
                        "Deaths": player['deaths'],
                        "Assists": player['assists'],
                        "KDA": f"{player['kills']}/{player['deaths']}/{player['assists']}",
                        "Dégâts": player['totalDamageDealtToChampions'],
                        "Dégâts (%)": player.get('challenges', {}).get('teamDamagePercentage', 0),

                        # Stats Tanking
                        "Dégâts Reçus": player.get('totalDamageTaken', 0),
                        "Dégâts Reçus (%)": player.get('challenges', {}).get('damageTakenOnTeamPercentage', 0),
                        "Dégâts Réduits sur soi": player.get('damageSelfMitigated', 0),

                        # Stats Farming & Gold
                        "Gold": player['goldEarned'],
                        "Nombre de CS": player.get('totalMinionsKilled', 0) + player.get('neutralMinionsKilled', 0),
                        "Nombre de CS par minute": round((player.get('totalMinionsKilled', 0) + player.get('neutralMinionsKilled', 0)) / (match['info']['gameDuration'] / 60), 2),
                        "Nombre de CS at 10": player.get('challenges', {}).get('laneMinionsFirst10Minutes', 0) + player.get('challenges', {}).get('jungleCsBefore10Minutes', 0),

                        # Stats Vision
                        "Score de Vision": player.get('visionScore', 0),
                        "Wards Placed": player.get('wardsPlaced', 0),                        
                    }
                    data_rows.append(row)
                    
    
    df = pd.DataFrame(data_rows)

    if not df.empty:
        # Nettoyage et ordonnancement des positions
        df['Position_Raw'] = pd.Categorical(df['Position_Raw'], categories=ROLE_ORDER, ordered=True)
        df = df.sort_values(by=['Game', 'Position_Raw'])

    return df, list(all_found_players)


# --- 3. Affichage Principal ---
if matches_data:
    df, all_players_list = process_files(matches_data)
    
    if df.empty:
        st.error("Aucun des joueurs ciblés n'a été trouvé dans les fichiers uploadés.")
        st.write("Joueurs trouvés : " + ", ".join(all_players_list))
    else:

        col1, col2 = st.columns([1,3])

        with col1:
            st.subheader("Paramètres")
            category = st.selectbox("Catégorie", list(STATS_CONFIG.keys()))
            stat_name = st.selectbox("Statistique", list(STATS_CONFIG[category].keys()))

            current_config = STATS_CONFIG[category][stat_name]
            y_axis_col = current_config["col"]

        with col2:
            st.subheader(current_config.get("title", y_axis_col))

            format_str = current_config.get("fmt", "%{y}")

            fig = px.bar(
                df,
                x="Joueur",
                y=y_axis_col,
                color="Game",
                text="Champion",
                title=f"{current_config["title"]} par joueur",
                hover_data={
                    "Game": True,
                    "Joueur": True,
                    "KDA": True,
                    "Champion": True,
                    y_axis_col: True # Affiche la valeur de la statistique en hover, y_axis_col ? au lieu de True
                },
                barmode="stack" #group = côte à côte, stack = empilé
            )

            fig.update_traces(texttemplate='%{text}<br>' + format_str, textposition='inside')
            fig.update_layout(height=600, xaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("Voir les données brutes"):
            st.dataframe(df)
