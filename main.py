import streamlit as st
import pandas as pd
import plotly.express as px
import statsmodels.api as sm
import datetime



# --- Configuration de la page Streamlit ---
st.set_page_config(page_title="Tableau de Bord Interactif", layout="wide")
st.title("📈 Tableau de Bord Interactif des Données de Santé")

# --- Ajout dans la sidebar ---
st.sidebar.header("🔍 Filtrage des données")
#date_debut = st.sidebar.date_input("Date de début", value=None)
date_debut = st.sidebar.date_input("Date de début", value=datetime.date(2024, 10, 1))

# --- SECTION PRESSION ---

st.write("### Pression")

# --- Chargement des données ---
try:
    # On essaie de lire le fichier CSV qui contient les données synthétisées
    df_synthese = pd.read_csv('synthese.csv')
    
    # Il est crucial de convertir la colonne 'Date-Heure' en vrai format de date
    # pour que Plotly puisse l'utiliser comme un axe temporel.
    df_synthese['Date-Heure'] = pd.to_datetime(df_synthese['Date-Heure'])
    
    st.success("Fichier `synthese.csv` chargé avec succès.")
    #st.write("### Aperçu des données utilisées pour les graphiques :")
    #st.dataframe(df_synthese.head())
    
   

# --- Filtrage des données si une date est sélectionnée ---
    if date_debut:
        # Conversion en datetime pour comparaison
        date_debut = pd.to_datetime(date_debut)
        df_synthese = df_synthese[df_synthese['Date-Heure'] >= date_debut]

    # --- Création des graphiques ---


    # === GRAPHIQUE 1 : PRESSION SYSTOLIQUE ET DIASTOLIQUE ===
    
    # Pour tracer Systolique et Diastolique sur le même graphique avec des couleurs différentes,
    # on transforme les données en format "long" avec la fonction melt de Pandas.
    df_pressure = df_synthese.melt(
        id_vars=['Date-Heure'], 
        value_vars=['Systolique (mmHg)', 'Diastolique (mmHg)'],
        var_name='Mesure', 
        value_name='Pression'
    )

    # Création de la figure avec Plotly Express. 
    # 'color="Mesure"' assigne automatiquement une couleur à 'Systolique' et une autre à 'Diastolique'.
    fig_pressure = px.scatter(
        df_pressure, 
        x='Date-Heure', 
        y='Pression', 
        color='Mesure',
        #markers=True, # Ajoute des points sur la ligne pour chaque mesure
        trendline='lowess', # Ajoute automatiquement les courbes de tendance
        title='Suivi de la Pression Artérielle (Systolique et Diastolique)',
        labels={
            "Date-Heure": "Date et Heure",
            "Pression": "Pression (mmHg)",
            "Mesure": "Type de Mesure"
        },
        color_discrete_map={
            'Systolique (mmHg)': 'red',
            'Diastolique (mmHg)': 'blue'
        }
    )
    
    # Affichage du premier graphique dans l'application Streamlit
    st.plotly_chart(fig_pressure, use_container_width=True)

    # Bouton téléchargement
    with open("blood.csv", "rb") as f:
    st.download_button(
        label="📥 Télécharger le fichier CSV",
        data=f,
        file_name="blood.csv",
        mime="text/csv"
    )

    # ---


    # === GRAPHIQUE 2 : POULS ===
    
    # Ce graphique est plus direct car il n'y a qu'une seule variable à tracer.
    fig_pulse = px.scatter(
        df_synthese, 
        x='Date-Heure', 
        y='Pouls (bpm)', 
        #markers=True, # Ajoute des points sur la ligne
        trendline='lowess', # Ajoute automatiquement les courbes de tendance
        title='Suivi de la fréquence cardiaque',
        labels={
            "Date-Heure": "Date et Heure",
            "Pouls (bpm)": "Pouls (battements par minute)"
        }
    )
    
    # On personnalise la couleur de la ligne pour la rendre distincte.
    fig_pulse.update_traces(line_color='green')

    # Affichage du second graphique dans l'application Streamlit
    st.plotly_chart(fig_pulse, use_container_width=True)

except FileNotFoundError:
    st.error(
        "❌ Le fichier `synthese.csv` n'a pas été trouvé. "
        "Veuillez d'abord générer ce fichier en utilisant la page d'analyse de données."
    )
except Exception as e:
    st.error(f"Une erreur est survenue lors du chargement ou de l'affichage des données : {e}")


# --- SECTION GLYCÉMIE ---

# --- Chargement des données ---
try:
    # On essaie de lire le fichier CSV qui contient les données synthétisées
    df_glycemie = pd.read_csv('glycemie.csv')
    
    # Il est crucial de convertir la colonne 'Date-Heure' en vrai format de date
    # pour que Plotly puisse l'utiliser comme un axe temporel.
    df_glycemie['Date-Heure'] = pd.to_datetime(df_glycemie['Date-Heure'])
    
    st.success("Fichier `glycemie.csv` chargé avec succès.")
    #st.write("### Aperçu des données utilisées pour les graphiques :")

    
    # --- Filtrage des données si une date est sélectionnée ---
    if date_debut:
        # Conversion en datetime pour comparaison
        date_debut = pd.to_datetime(date_debut)
        df_glycemie = df_glycemie[df_glycemie['Date-Heure'] >= date_debut]


    # --- Création des graphiques ---


    # === GRAPHIQUE 1 : PRESSION SYSTOLIQUE ET DIASTOLIQUE ===


    # Création de la figure avec Plotly Express. 

    fig_glycemie = px.scatter(
        df_glycemie, 
        x='Date-Heure', 
        y='Glycémie (mmol/L)', 
        trendline='lowess', # Ajoute automatiquement les courbes de tendance
        title='Suivi de la Glycémie',
        labels={
            "Date-Heure": "Date et Heure",
            "Pression": "Pression (mmHg)",
            "Mesure": "Type de Mesure"
        },
        
    )
    
    # Affichage du premier graphique dans l'application Streamlit
    st.plotly_chart(fig_glycemie, use_container_width=True)

    

except FileNotFoundError:
    st.error(
        "❌ Le fichier `synthese.csv` n'a pas été trouvé. "
        "Veuillez d'abord générer ce fichier en utilisant la page d'analyse de données."
    )
except Exception as e:
    st.error(f"Une erreur est survenue lors du chargement ou de l'affichage des données : {e}")


    # --- SECTION POIDS ---


# --- Chargement des données ---
try:
    # On essaie de lire le fichier CSV qui contient les données synthétisées
    df_poids = pd.read_csv('poids.csv')
    
    # Il est crucial de convertir la colonne 'Date' en vrai format de date
    # pour que Plotly puisse l'utiliser comme un axe temporel.
    df_poids['Date'] = pd.to_datetime(df_poids['Date'])
    
    st.success("Fichier `poids.csv` chargé avec succès.")

    # --- Filtrage des données si une date est sélectionnée ---
    if date_debut:
        # Conversion en datetime pour comparaison
        date_debut = pd.to_datetime(date_debut)
        df_poids = df_poids[df_poids['Date'] >= date_debut]

    # --- Création des graphiques ---


    # Création de la figure avec Plotly Express. 

    fig_poids = px.scatter(
        df_poids, 
        x='Date', 
        y='Poids_lbs', 
        trendline='lowess', # Ajoute automatiquement les courbes de tendance
        title='Suivi du poids',
        labels={
            "Date-Heure": "Date et Heure",
            "Pression": "Poids (lbs)",
            "Mesure": "Type de Mesure"
        },
        
    )
    
    # Affichage du premier graphique dans l'application Streamlit
    st.plotly_chart(fig_poids, use_container_width=True)

    

except FileNotFoundError:
    st.error(
        "❌ Le fichier `poids.csv` n'a pas été trouvé. "
        "Veuillez d'abord générer ce fichier en utilisant la page d'analyse de données."
    )
except Exception as e:
    st.error(f"Une erreur est survenue lors du chargement ou de l'affichage des données : {e}")

