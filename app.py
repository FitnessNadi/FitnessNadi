import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(layout="wide")
st.title("Vegane Gesundheits- & Nährstoff-App")

# Einlesen der Nährstoffdatenbank
nutrients = pd.read_csv("vegan_naehrstoffe.csv")

# Empfohlene Tageswerte (ungefähr, Erwachsene, weiblich)
reference = {
    "Eisen (mg)": 15,
    "Magnesium (mg)": 310,
    "Kalzium (mg)": 1000,
    "Protein (g)": 50
}

# Nährstoffanalyse aus eingegebenem Text
def analysiere_ernaehrung(text):
    text = text.lower()
    gesamt = {n: 0 for n in reference}
    for _, row in nutrients.iterrows():
        if row["Lebensmittel"].lower() in text:
            for n in reference:
                gesamt[n] += row[n]
    return gesamt

# Eingabe für einen Tag
heute = datetime.date.today()
st.header(f"Tagesplanung – {heute.strftime('%A, %d.%m.%Y')}")

essen = st.text_area("Was hast du heute gegessen? (z. B. Haferflocken, Brokkoli, Tofu)")

if st.button("Nährstoffanalyse starten"):
    resultate = analysiere_ernaehrung(essen)
    st.subheader("Deine geschätzte Nährstoffzufuhr heute:")
    for n, wert in resultate.items():
        bedarf = reference[n]
        prozent = round((wert / bedarf) * 100)
        status = "OK" if prozent >= 90 else "Niedrig"
        st.write(f"{n}: {wert:.1f} mg/g ({prozent}% des Bedarfs) – **{status}**")

    if resultate["Eisen (mg)"] < 10:
        st.info("Tipp: Erhöhe deine Eisenaufnahme z. B. mit Linsen, Tofu oder Spinat.")
    if resultate["Kalzium (mg)"] < 700:
        st.info("Tipp: Kalziumreiche Optionen sind angereicherte Pflanzenmilch, Brokkoli oder Mandeln.")
