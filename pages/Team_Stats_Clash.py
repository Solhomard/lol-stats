import streamlit as st
import json
import pandas as pd
import plotly.express as px
import os

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
                        "Dégâts": player['totalDamageDealtToChampions'],
                        "Dégâts (%)": player.get('challenges', {}).get('teamDamagePercentage', 0),
                        "Dégâts Reçus": player.get('totalDamageTaken', 0),
                        "Dégâts Reçus (%)": player.get('challenges', {}).get('damageTakenOnTeamPercentage', 0),
                        "Dégâts Réduits sur soi": player.get('damageSelfMitigated', 0),
                        "Gold": player['goldEarned'],
                        "Score de Vision": player.get('visionScore', 0),
                        "Nombre de CS": player.get('totalMinionsKilled', 0) + player.get('neutralMinionsKilled', 0),
                        "Nombre de CS par minute": round((player.get('totalMinionsKilled', 0) + player.get('neutralMinionsKilled', 0)) / (match['info']['gameDuration'] / 60), 2),
                        "Nombre de CS at 10": player.get('challenges', {}).get('laneMinionsFirst10Minutes', 0) + player.get('challenges', {}).get('jungleCsBefore10Minutes', 0),
                        "Kills": player['kills'],
                        "Deaths": player['deaths'],
                        "Assists": player['assists'],
                        "KDA": f"{player['kills']}/{player['deaths']}/{player['assists']}"
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
        # Sélecteur de stat
        stat_choice = st.radio(
            "Quelle statistique afficher ?",
            ["Kills", "Deaths", "Assists", "Dégâts", "Dégâts (%)", "Dégâts Reçus", "Dégâts Reçus (%)", "Dégâts Réduits sur soi", "Nombre de CS", "Nombre de CS par minute", "Nombre de CS%10", "Score de Vision", "Gold"],
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
        elif stat_choice == "Dégâts Reçus":
            y_axis = "Dégâts Reçus"
            title = "Dégâts reçus totaux par partie"
            text_format = "%{y:.2s}" # Format compact (25k)
        elif stat_choice == "Dégâts Reçus (%)":
            y_axis = "Dégâts Reçus (%)"
            title = "Pourcentage des dégâts reçus de l'équipe"
            text_format = "%{y:.1%}" # Format pourcentage
        elif stat_choice == "Dégâts Réduits sur soi":
            y_axis = "Dégâts Réduits sur soi"
            title = "Dégâts réduits par le joueur"
            text_format = "%{y}" # Format plus précis
        elif stat_choice == "Score de Vision":
            y_axis = "Score de Vision"
            title = "Score de Vision par partie"
            text_format = "%{y}"
        elif stat_choice == "Nombre de CS":
            y_axis = "Nombre de CS"
            title = "Nombre de CS par partie"
            text_format = "%{y}"
        elif stat_choice == "Nombre de CS par minute":
            y_axis = "Nombre de CS par minute"
            title = "Nombre de CS par minute"
            text_format = "%{y:.1f}"
        elif stat_choice == "Nombre de CS%10":
            y_axis = "Nombre de CS at 10"
            title = "Nombre de CS à 10 minutes"
            text_format = "%{y}"
        elif stat_choice == "Kills":
            y_axis = "Kills"
            title = "Kills par partie"
            text_format = "%{y}"
        elif stat_choice == "Deaths":
            y_axis = "Deaths"
            title = "Deaths par partie"
            text_format = "%{y}"
        elif stat_choice == "Assists":
            y_axis = "Assists"
            title = "Assists par partie"
            text_format = "%{y}"
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