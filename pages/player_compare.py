import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Comparaison Joueurs")
st.title("⚔️ Comparateur de Joueurs")

TARGET_PLAYERS = ["Magical craft", "Frozabys", "LeDoréLoup", "KatastrOhfiak", "Ohfiak"]
ROLE_ORDER = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
matches_data = []

if 'matches_data' not in st.session_state or not st.session_state['matches_data']:
    st.error("Données manquantes. Allez à l'Accueil.")
else:
    matches_data = st.session_state['matches_data']

def process_comparison(matches):
    # Extraction des données spécifiques pour la comparaison
    data_rows = []
    for i, match in enumerate(matches):
         
         game_label = f"Game {i+1}"

         if 'info' in match and 'participants' in match['info']:
            for p in match['info']['participants']:
                name = p.get('riotIdGameName','')
                if name in TARGET_PLAYERS:
                    data_rows.append({
                        "Game": game_label,
                        "Joueur": name,
                        "Champion": p['championName'],
                        "Gold Share": p['goldEarned'], # Simplifié pour l'exemple
                        "Damage Share": p['totalDamageDealtToChampions'],
                        "Damage Percentage": p.get('challenges', {}).get('teamDamagePercentage', 0),
                        "Damage Reçus": p.get('totalDamageTaken', 0),
                        "Damage Réduits sur soi": p.get('damageSelfMitigated', 0),
                        "Damage aux Objectifs": p.get('damageDealtToObjectives', 0),
                        "Vision Score": p.get('visionScorePerMinute', 0),
                        "Morts": p['deaths'],
                        "Heal Total": p.get('totalHeal', 0)
                    })

    df = pd.DataFrame(data_rows)
    return df

if matches_data:
    df = process_comparison(matches_data)

    with st.container():
        st.subheader("Données des Joueurs")
        category = st.pills("Catégorie", ["Or vs Dégâts"], key="category_pills")

    # Graphique avancé
    st.subheader("Efficacité Gold / Dégâts")
    fig = px.scatter(
        df, 
        x="Gold Share", 
        y="Damage Share", 
        color="Game", 
        hover_data=["Joueur", "Champion"],
        #trendline="ols",
        title="Qui convertit le mieux son or en dégâts ?"
    )
    st.plotly_chart(fig)

