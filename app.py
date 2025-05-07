import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(layout="wide")
st.title("Vegane Gesundheits- & Nährstoff-Analyse-App")

# Daten laden
nutri_df = pd.read_csv("vegan_naehrstoffe.csv")

# Tagesplan-Eingabe
st.header("Heutige Mahlzeiten")
essen = st.text_area("Was hast du heute gegessen? (z. B. Haferflocken, Linsen, Spinat)")

# Einfache Analyse basierend auf bekannten Lebensmitteln
def analysiere_naehrstoffe(text):
    text = text.lower()
    result = {n: 0 for n in ["Eisen_mg", "Magnesium_mg", "Kalzium_mg", "Zink_mg", "Protein_g"]}
    lebensmittel_erkannt = []
    for i, row in nutri_df.iterrows():
        if row["Lebensmittel"].lower() in text:
            lebensmittel_erkannt.append(row["Lebensmittel"])
            for n in result:
                result[n] += row[n]
    return result, lebensmittel_erkannt

if essen:
    werte, zutaten = analysiere_naehrstoffe(essen)
    st.subheader("Erkannte Zutaten:")
    st.write(", ".join(zutaten) if zutaten else "Keine passenden Lebensmittel erkannt.")
    
    st.subheader("Geschätzte Nährstoffzufuhr (gesamt):")
    referenz = {
        "Eisen_mg": 15,
        "Magnesium_mg": 300,
        "Kalzium_mg": 1000,
        "Zink_mg": 8,
        "Protein_g": 50
    }

    for n, val in werte.items():
        ziel = referenz[n]
        prozent = round(val / ziel * 100)
        if prozent >= 100:
            status = "ausreichend"
        elif prozent >= 70:
            status = "ok"
        else:
            status = "zu wenig"
        st.write(f"{n.replace('_mg','').replace('_g','').capitalize()}: {val:.1f} ({prozent}% des Bedarfs) → {status}")
