import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(layout="wide")
st.title("Vegane Gesundheits- & Nährstoff-App mit Planung")

DATA_FILE = "tagebuch.csv"
NUTRIENT_FILE = "vegan_naehrstoffe.csv"

# Referenzwerte (weiblich, ca.)
reference = {
    "Eisen (mg)": 15,
    "Magnesium (mg)": 310,
    "Kalzium (mg)": 1000,
    "Protein (g)": 50
}

# Lade Nährstoffdatenbank
nutrients = pd.read_csv(NUTRIENT_FILE)

def analysiere_ernaehrung(text):
    text = text.lower()
    gesamt = {n: 0 for n in reference}
    for _, row in nutrients.iterrows():
        if row["Lebensmittel"].lower() in text:
            for n in reference:
                gesamt[n] += row[n]
    return gesamt

# Initialwerte
if "vitamine" not in st.session_state:
    st.session_state.vitamine = ["Magnesium", "Vitamin D", "Omega 3"]
if "zyklus_start" not in st.session_state:
    st.session_state.zyklus_start = datetime.date.today()
if "zyklus_länge" not in st.session_state:
    st.session_state.zyklus_länge = 28

# Zyklusphase berechnen
def get_zyklusphase(datum, start, länge):
    tage_seit_start = (datum - start).days % länge
    if tage_seit_start < 5:
        return "Periode"
    elif 5 <= tage_seit_start < 13:
        return "Follikelphase"
    elif 13 <= tage_seit_start < 16:
        return "Eisprung"
    elif 16 <= tage_seit_start < länge:
        return "Lutealphase"
    return "Unbekannt"

# Lade CSV-Daten
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, parse_dates=["Datum"])
else:
    df = pd.DataFrame(columns=["Datum", "Essen geplant", "Essen gegessen", "Sport geplant", "Sport gemacht"] + st.session_state.vitamine)

# Sidebar-Einstellungen
st.sidebar.header("Zyklus-Einstellungen")
zyklus_start = st.sidebar.date_input("Erster Tag der letzten Periode", st.session_state.zyklus_start)
zyklus_länge = st.sidebar.number_input("Zykluslänge (Tage)", 20, 40, st.session_state.zyklus_länge)
st.session_state.zyklus_start = zyklus_start
st.session_state.zyklus_länge = zyklus_länge

# Woche anzeigen
heute = datetime.date.today()
woche = [heute + datetime.timedelta(days=i) for i in range(7)]

st.header("Wochenübersicht")

for tag in woche:
    tag_str = str(tag)
    eintrag = df[df["Datum"] == pd.to_datetime(tag_str)]
    if not eintrag.empty:
        eintrag = eintrag.iloc[0]
    else:
        eintrag = {}

    with st.expander(f"{tag.strftime('%A, %d.%m.%Y')} – {get_zyklusphase(tag, zyklus_start, zyklus_länge)}"):
        essen_geplant = st.text_area("Essen geplant", eintrag.get("Essen geplant", ""), key=f"essen_geplant_{tag}")
        essen_ist = st.text_area("Essen gegessen", eintrag.get("Essen gegessen", ""), key=f"essen_ist_{tag}")
        sport_geplant = st.text_input("Sport geplant", eintrag.get("Sport geplant", ""), key=f"sport_geplant_{tag}")
        sport_ist = st.text_input("Sport gemacht", eintrag.get("Sport gemacht", ""), key=f"sport_ist_{tag}")

        vitamin_daten = {}
        for v in st.session_state.vitamine:
            vitamin_daten[v] = st.checkbox(f"{v} genommen", value=eintrag.get(v, "") == "ja", key=f"{v}_{tag}")

        if st.button(f"Speichern für {tag}", key=f"save_{tag}"):
            new_row = {
                "Datum": pd.to_datetime(tag_str),
                "Essen geplant": essen_geplant,
                "Essen gegessen": essen_ist,
                "Sport geplant": sport_geplant,
                "Sport gemacht": sport_ist,
            }
            for v in st.session_state.vitamine:
                new_row[v] = "ja" if vitamin_daten[v] else "nein"

            df = df[df["Datum"] != pd.to_datetime(tag_str)]
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"Eintrag für {tag.strftime('%d.%m.%Y')} gespeichert.")

        # Nährstoffanalyse anzeigen
        st.subheader("Vegane Nährstoffanalyse")
        resultate = analysiere_ernaehrung(essen_ist)
        for n, wert in resultate.items():
            bedarf = reference[n]
            prozent = round((wert / bedarf) * 100)
            status = "OK" if prozent >= 90 else "Niedrig"
            st.write(f"{n}: {wert:.1f} ({prozent}% des Bedarfs) – **{status}**")

# Sidebar: Vitaminliste bearbeiten
st.sidebar.header("Vitaminliste bearbeiten")
neues_vitamin = st.sidebar.text_input("Neues Vitamin hinzufügen")
if st.sidebar.button("Hinzufügen") and neues_vitamin:
    if neues_vitamin not in st.session_state.vitamine:
        st.session_state.vitamine.append(neues_vitamin)
        st.experimental_rerun()

if st.sidebar.button("App zurücksetzen (nur Session)"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()
