import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuration de la Page Streamlit ---
st.set_page_config(page_title="Suivi de Glycémie", layout="wide")

# --- Titre de la Page ---
st.title("🩸 Suivi de Glycémie")
st.markdown("---")

# --- Section 1: Importation et Sélection des Données ---
st.header("1. Importer votre fichier de données")

uploaded_file = st.file_uploader(
    "Choisissez un fichier CSV",
    type="csv",
    help="Le fichier doit contenir des colonnes pour la date, la glycémie et des notes."
)

if uploaded_file is not None:
    try:
        df_input = pd.read_csv(uploaded_file, dtype=str).fillna('')
        st.success("Fichier importé avec succès ! Voici un aperçu :")
        st.dataframe(df_input.head())

        st.markdown("---")
        st.header("2. Associer vos colonnes")

        st.info('**Note :** Le format attendu pour la date-heure est `J MMM AAAA, HH "h" MM` (ex: `3 sept. 2025, 09 h 51`).')

        with st.form("column_selection_form"):
            available_columns = df_input.columns.tolist()
            col_datetime = st.selectbox("Colonne pour la date et l'heure :", available_columns)
            col_glucose = st.selectbox("Colonne pour la Glycémie (mmol/L) :", available_columns)
            col_note1 = st.selectbox("Colonne pour la Note 1 :", available_columns)
            col_note2 = st.selectbox("Colonne pour la Note 2 :", available_columns)
            submit_button = st.form_submit_button(label="Valider et Enregistrer les Données")

        if submit_button:
            df_processed = df_input[[col_datetime, col_glucose, col_note1, col_note2]].copy()
            df_processed.columns = ["Date-Heure", "Glycémie (mmol/L)", "Note-1", "Note-2"]

            # --- MODIFICATION CLÉ : Remplacement manuel des noms de mois ---
            
            # 1. Définir les correspondances pour les mois
            month_map = {
                "janv.": "01", "févr.": "02", "mars": "03", "avr.": "04",
                "mai": "05", "juin": "06", "juill.'": "07", "juill.": "07",
                "août": "08", "sept.": "09", "oct.": "10", "nov.": "11", "déc.": "12"
            }

            # 2. Remplacer chaque abréviation de mois par son numéro
            # On s'assure que la colonne est bien une chaîne de caractères pour utiliser .replace
            date_series = df_processed["Date-Heure"].astype(str)
            for month_str, month_num in month_map.items():
                date_series = date_series.str.replace(month_str, month_num, regex=False)

            # 3. Définir le nouveau format de date qui attend un numéro de mois (%m)
            date_format_string = "%d %m %Y, %H h %M"

            # 4. Convertir la colonne en datetime avec le format correct
            df_processed["Date-Heure"] = pd.to_datetime(
                date_series,
                format=date_format_string,
                errors='coerce'
            )
            # --- FIN DE LA MODIFICATION ---

            df_processed.dropna(subset=["Date-Heure"], inplace=True)
            
            csv_path = "glycemie.csv"
            if os.path.exists(csv_path):
                df_existing = pd.read_csv(csv_path, parse_dates=["Date-Heure"])
                df_combined = pd.concat([df_existing, df_processed], ignore_index=True)
                df_combined.drop_duplicates(subset=["Date-Heure"], keep='last', inplace=True)
                df_combined.sort_values(by="Date-Heure", inplace=True)
                df_combined.to_csv(csv_path, index=False)
                st.success(f"Données ajoutées avec succès au fichier **{csv_path}** !")
            else:
                df_processed.sort_values(by="Date-Heure", inplace=True)
                df_processed.to_csv(csv_path, index=False)
                st.success(f"Le fichier **{csv_path}** a été créé avec vos données !")
            
            st.session_state.processed = True

    except Exception as e:
        st.error(f"Une erreur est survenue lors du traitement : {e}")
        st.warning("Vérifiez que le format de date dans votre fichier correspond bien au format attendu et que les colonnes sélectionnées sont les bonnes.")

# --- Section 3: Visualisation des Données ---
st.markdown("---")
st.header("3. Graphique de suivi de la glycémie")

if os.path.exists("glycemie.csv"):
    try:
        df_final = pd.read_csv("glycemie.csv", parse_dates=["Date-Heure"])
        if not df_final.empty and len(df_final) > 1: # Il faut au moins 2 points pour une tendance
            st.write("Graphique de la glycémie en fonction du temps, avec sa courbe de tendance.")
            
            # --- MODIFICATION CLÉ : Ajout de la courbe de tendance ---
            fig = px.scatter(
                df_final,
                x="Date-Heure",
                y="Glycémie (mmol/L)",
                title="Évolution de la Glycémie avec Courbe de Tendance",
                labels={"Date-Heure": "Date et Heure"},
                trendline="lowess", # Ajoute une ligne de tendance (régression linéaire)
                trendline_color_override="red" # Optionnel: pour que la ligne soit bien visible
            )
            
            # On ajoute la ligne des points pour ne pas perdre la vue détaillée
            fig.add_scatter(
                x=df_final["Date-Heure"],
                y=df_final["Glycémie (mmol/L)"],
                mode='lines+markers',
                name='Mesures'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Afficher les données enregistrées dans glycemie.csv"):
                st.dataframe(df_final)
        elif not df_final.empty:
            st.warning("Il faut au moins deux points de données pour dessiner une courbe de tendance.")
            st.dataframe(df_final)
        else:
            st.info("Le fichier `glycemie.csv` est vide.")
    except Exception as e:
        st.error(f"Impossible d'afficher le graphique. Erreur : {e}")
else:
    st.info("Veuillez importer un fichier pour afficher le graphique.")