import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Comparaison Joueurs")

if 'matches_data' not in st.session_state or not st.session_state['matches_data']:
    st.error("Données manquantes. Allez à l'Accueil.")
else:
    matches = st.session_state['matches_data']
    matches += st.session_state['matches_data_file']
    st.title("⚔️ Comparateur de Joueurs")

if 'matches_data_file' not in st.session_state or not st.session_state['matches_data_file']:
    st.error("Données manquantes. Allez à l'Accueil.")
else:
    matches = st.session_state['matches_data_file']
    st.title("⚔️ Comparateur de Joueurs")

    # Extraction des données spécifiques pour la comparaison
    data_rows = []
    for match in matches:
         if 'info' in match and 'participants' in match['info']:
            for p in match['info']['participants']:
                data_rows.append({
                    "Joueur": p['summonerName'] if p['summonerName'] else p['riotIdGameName'],
                    "Gold Share": p['goldEarned'], # Simplifié pour l'exemple
                    "Damage Share": p['totalDamageDealtToChampions']
                })

    df = pd.DataFrame(data_rows)

    # Graphique avancé
    st.subheader("Efficacité Gold / Dégâts")
    fig = px.scatter(
        df, 
        x="Gold Share", 
        y="Damage Share", 
        color="Joueur", 
        hover_data=["Joueur"],
        title="Qui convertit le mieux son or en dégâts ?"
    )
    st.plotly_chart(fig)