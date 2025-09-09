import streamlit as st
import pandas as pd
import os
import plotly.express as px
import numpy as np
from datetime import datetime
import ruptures as rpt  # <-- pour la détection des ruptures

st.title("📊 Suivi du Poids")

# --- Charger fichier d'entrée ---
uploaded_file = st.file_uploader("📂 Importer un fichier CSV ou Excel", type=["csv", "xlsx"])

if uploaded_file:
    # Lire fichier
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Aperçu des données importées :")
    st.dataframe(df.head())

    # Sélection colonnes
    col_date = st.selectbox("📅 Sélectionner la colonne Date-Heure", df.columns)
    col_kg = st.selectbox("⚖️ Sélectionner la colonne Poids (kg)", df.columns)
    col_lbs = st.selectbox("⚖️ Sélectionner la colonne Poids (lbs)", df.columns)

    if st.button("✅ Ajouter au fichier poids.csv"):
        new_data = df[[col_date, col_kg, col_lbs]].copy()
        new_data[col_date] = pd.to_datetime(new_data[col_date], errors="coerce")
        new_data = new_data.dropna()

        # Renommer les colonnes
        new_data.columns = ["Date", "Poids_kg", "Poids_lbs"]

        # Ajouter au fichier existant ou créer
        if os.path.exists("poids.csv"):
            existing = pd.read_csv("poids.csv", parse_dates=["Date"])
            combined = pd.concat([existing, new_data]).drop_duplicates().sort_values("Date")
        else:
            combined = new_data

        combined.to_csv("poids.csv", index=False)
        st.success("✅ Données mises à jour dans poids.csv")

# --- Graphique ---
if os.path.exists("poids.csv"):
    data = pd.read_csv("poids.csv", parse_dates=["Date"]).sort_values("Date")

    unit = st.radio("Unité d'affichage :", ["kg", "lbs"])
    y_col = "Poids_kg" if unit == "kg" else "Poids_lbs"

    # --- Sélection date de début ---
    min_date = data["Date"].min().date()
    max_date = data["Date"].max().date()
    start_date = st.date_input("📅 Date de début du graphique", value=min_date, min_value=min_date, max_value=max_date)

    # Filtrer les données à partir de la date choisie
    data = data[data["Date"] >= pd.to_datetime(start_date)]

    # Graphique principal
    fig = px.scatter(data, x="Date", y=y_col, title=f"Évolution du poids ({unit})", trendline="ols")

    # --- Détection des ruptures avec ruptures ---
    signal = data[y_col].values

    if len(signal) > 5:  # éviter erreur si trop peu de points
        pen = st.slider("Sensibilité détection de tendance (pen)", 1, 20, 5)
        model = rpt.Pelt(model="rbf").fit(signal)
        breakpoints = model.predict(pen=pen)

        # Ajouter segments de tendance
        for i in range(len(breakpoints)-1):
            start, end = (0 if i == 0 else breakpoints[i-1]), breakpoints[i]
            seg_x = data["Date"].iloc[start:end]
            seg_y = data[y_col].iloc[start:end]

            if len(seg_x) > 1:
                coef = np.polyfit(range(len(seg_x)), seg_y, 1)
                trend_line = np.poly1d(coef)(range(len(seg_x)))
                fig.add_scatter(x=seg_x, y=trend_line, mode="lines", name=f"Tendance {i+1}")

    # --- Ajouter des étiquettes personnalisées ---
    st.subheader("📝 Ajouter une étiquette")
    label_date = st.date_input("Date de l'étiquette")
    label_text = st.text_input("Texte de l'étiquette")

    if st.button("📍 Ajouter l'étiquette au graphique"):
        fig.add_annotation(
            x=pd.to_datetime(label_date),
            y=float(data[y_col].iloc[-1]),  # approx dernier poids
            text=label_text,
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-40
        )

    st.plotly_chart(fig, use_container_width=True)
