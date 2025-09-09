import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import timedelta

# --- Fonctions Utilitaires ---

def process_and_save_data(df_processed, csv_path="blood.csv"):
    """
    Traite et sauvegarde les données dans le fichier blood.csv.
    """
    df_processed["Date-Heure"] = pd.to_datetime(df_processed["Date-Heure"], errors='coerce')
    df_processed.dropna(subset=["Date-Heure"], inplace=True)

    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path, parse_dates=["Date-Heure"])
        df_combined = pd.concat([df_existing, df_processed], ignore_index=True)
        df_combined.drop_duplicates(subset=["Date-Heure"], keep='last', inplace=True)
        df_combined.sort_values(by="Date-Heure", inplace=True)
        df_combined.to_csv(csv_path, index=False)
        st.success(f"Données ajoutées avec succès à **{csv_path}** !")
    else:
        df_processed.sort_values(by="Date-Heure", inplace=True)
        df_processed.to_csv(csv_path, index=False)
        st.success(f"Le fichier **{csv_path}** a été créé avec vos données !")
    
    st.session_state.processed = True

def generate_synthesis_v2(input_path="blood.csv", output_path="synthese.csv"):
    """
    NOUVELLE LOGIQUE : Analyse blood.csv pour créer un fichier de synthèse.
    Identifie des groupes de mesures prises à moins de 30 minutes d'intervalle,
    puis conserve la ligne avec la valeur systolique la plus basse de chaque groupe.
    """
    if not os.path.exists(input_path):
        st.error(f"Le fichier '{input_path}' est introuvable.")
        return None

    df = pd.read_csv(input_path, parse_dates=["Date-Heure"])
    if df.empty:
        st.warning(f"Le fichier '{input_path}' est vide.")
        return None

    # S'assurer que les données sont triées par date pour que l'analyse soit correcte
    df = df.sort_values(by="Date-Heure").reset_index(drop=True)

    # Calculer la différence de temps entre une mesure et la précédente
    time_diff = df["Date-Heure"].diff()

    # Identifier le début de chaque nouveau groupe (écart > 30 mins)
    # cumsum() crée un identifiant unique pour chaque groupe
    group_ids = (time_diff > timedelta(minutes=30)).cumsum()

    # Appliquer la logique : pour chaque groupe, trouver l'index de la valeur systolique la plus basse
    idx_to_keep = df.groupby(group_ids)['Systolique (mmHg)'].idxmin()

    # Créer le DataFrame de synthèse en utilisant ces index
    df_synthese = df.loc[idx_to_keep]

    df_synthese.to_csv(output_path, index=False)
    
    return df_synthese

# --- Configuration de la Page Streamlit ---
st.set_page_config(page_title="Suivi de Pression Artérielle", layout="wide")
st.title("📊 Analyseur de Pression Artérielle")
st.markdown("---")

# --- Sections 1 & 2 : Importation et Traitement ---
st.header("1. Importer votre fichier de données")
uploaded_file = st.file_uploader("Choisissez un fichier XLSX", type="xlsx")

if uploaded_file is not None:
    try:
        df_input = pd.read_excel(uploaded_file)
        st.success("Fichier importé ! Voici un aperçu :")
        st.dataframe(df_input.head())

        st.markdown("---")
        st.header("2. Associer vos colonnes")

        with st.form("column_selection_form"):
            available_columns = df_input.columns.tolist()
            col_datetime = st.selectbox("Colonne Date et Heure :", available_columns)
            col_systolic = st.selectbox("Colonne Pression Systolique (mmHg) :", available_columns)
            col_diastolic = st.selectbox("Colonne Pression Diastolique (mmHg) :", available_columns)
            col_pulse = st.selectbox("Colonne Pouls (bpm) :", available_columns)
            col_notes = st.selectbox("Colonne Notes :", available_columns)
            submit_button = st.form_submit_button(label="Valider et Enregistrer dans blood.csv")

        if submit_button:
            df_processed = df_input[[col_datetime, col_systolic, col_diastolic, col_pulse, col_notes]].copy()
            df_processed.columns = ["Date-Heure", "Systolique (mmHg)", "Diastolique (mmHg)", "Pouls (bpm)", "Notes"]
            process_and_save_data(df_processed)

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")

# --- Section 3: Visualisation des Données Brutes ---
st.markdown("---")
st.header("3. Graphique des Données Brutes (`blood.csv`)")

if os.path.exists("blood.csv"):
    df_raw = pd.read_csv("blood.csv", parse_dates=["Date-Heure"])
    if not df_raw.empty:
        fig_raw = px.line(df_raw, x="Date-Heure", y=["Systolique (mmHg)", "Diastolique (mmHg)", "Pouls (bpm)"],
                          title="Évolution de Toutes les Mesures", markers=True,
                          labels={"value": "Mesure", "Date-Heure": "Date et Heure"})
        fig_raw.update_layout(legend_title_text='Indicateurs')
        st.plotly_chart(fig_raw, use_container_width=True)
    else:
        st.info("Le fichier `blood.csv` est vide.")
else:
    st.info("Aucune donnée brute à afficher. Veuillez importer un fichier.")

# --- Section 4: Analyse et Synthèse ---
st.markdown("---")
st.header("4. Analyse et Synthèse ✨")
st.markdown("""
Cliquez sur le bouton pour analyser `blood.csv`. Le script va identifier les groupes de mesures effectuées en moins de 30 minutes d'intervalle, 
et pour chaque groupe, il ne conservera que la mesure avec la **pression systolique la plus basse**.
Le résultat sera sauvegardé dans `synthese.csv` et un nouveau graphique sera affiché.
""")

if os.path.exists("blood.csv"):
    if st.button("Lancer l'analyse et créer synthese.csv"):
        with st.spinner("Analyse en cours..."):
            # Utilisation de la nouvelle fonction
            df_synthese = generate_synthesis_v2() 
            
            if df_synthese is not None:
                st.success("Fichier `synthese.csv` généré avec succès !")
                
                # Sauvegarder les données dans la session pour les réafficher sans recalculer
                st.session_state.df_synthese = df_synthese 
                
# Afficher les résultats si la synthèse a été générée
if 'df_synthese' in st.session_state:
    df_synthese = st.session_state.df_synthese
    
    st.subheader("Données de Synthèse (`synthese.csv`)")
    st.dataframe(df_synthese)
    
    # Bouton de téléchargement
    csv_data = df_synthese.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Télécharger synthese.csv", data=csv_data,
                       file_name='synthese.csv', mime='text/csv')

    #  # --- NOUVEAU GRAPHIQUE DE SYNTHESE ---
    # st.subheader("Graphique des Données de Synthèse")
    # fig_synth = px.line(df_synthese, x="Date-Heure", y=["Systolique (mmHg)", "Diastolique (mmHg)", "Pouls (bpm)"],
    #                     title="Évolution des Mesures Synthétisées", markers=True,
    #                     labels={"value": "Mesure", "Date-Heure": "Date et Heure"})
    # fig_synth.update_layout(legend_title_text='Indicateurs')
    # st.plotly_chart(fig_synth, use_container_width=True)

    # === GRAPHIQUE 1 : PRESSION SYSTOLIQUE ET DIASTOLIQUE ===
        
    # Pour tracer plusieurs lignes (systolique, diastolique) avec Plotly Express,
    # il est plus simple de "réorganiser" les données d'un format large à un format long.
    df_pressure = df_synthese.melt(id_vars=['Date-Heure'], 
                            value_vars=['Systolique (mmHg)', 'Diastolique (mmHg)'],
                            var_name='Mesure', 
                            value_name='Pression')

    # Création du graphique de pression
    fig_pressure = px.scatter(df_pressure, 
                                x='Date-Heure', 
                                y='Pression', 
                                color='Mesure', # Crée une couleur par mesure (Systolique/Diastolique)
                                title='Pression Artérielle avec Courbes de Tendance',
                                labels={'Date-Heure': 'Date et Heure', 'Pression': 'Pression (mmHg)'},
                                trendline='lowess', # Ajoute automatiquement les courbes de tendance
                                color_discrete_map={ # Personnaliser les couleurs
                                    'Systolique (mmHg)': 'red',
                                    'Diastolique (mmHg)': 'blue'
                                },
                                trendline_color_override="pink" # Optionnel: pour que la ligne soit bien visible
                                )
                                

    st.plotly_chart(fig_pressure, use_container_width=True)


    # === GRAPHIQUE 2 : POULS ===

    # La création du graphique du pouls est directe
    fig_pulse = px.scatter(df_synthese, 
                            x='Date-Heure', 
                            y='Pouls (bpm)', 
                            title='Pouls avec Courbe de Tendance',
                            labels={'Date-Heure': 'Date et Heure', 'Pouls (bpm)': 'Pouls (bpm)'},
                            trendline='lowess') # Ajoute la courbe de tendance

    # Pour une meilleure lisibilité, on peut changer la couleur
    fig_pulse.update_traces(marker=dict(color='green'))

    st.plotly_chart(fig_pulse, use_container_width=True)
