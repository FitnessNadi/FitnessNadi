import streamlit as st
import pandas as pd
import datetime

st.set_page_config(layout="wide")
st.title("Gesundheits- & Planungs-App")

# Initialdaten
if "vitamine" not in st.session_state:
    st.session_state.vitamine = ["Magnesium", "Vitamin D", "Omega 3"]
if "zyklus_start" not in st.session_state:
    st.session_state.zyklus_start = datetime.date.today()
if "zyklus_länge" not in st.session_state:
    st.session_state.zyklus_länge = 28

# Funktion: Zyklusphase berechnen
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

# Eingaben
st.sidebar.header("Zyklus-Einstellungen")
zyklus_start = st.sidebar.date_input("Erster Tag der letzten Periode", st.session_state.zyklus_start)
zyklus_länge = st.sidebar.number_input("Zykluslänge (Tage)", 20, 40, st.session_state.zyklus_länge)

st.session_state.zyklus_start = zyklus_start
st.session_state.zyklus_länge = zyklus_länge

# Wochendarstellung
heute = datetime.date.today()
woche = [heute + datetime.timedelta(days=i) for i in range(7)]

st.header("Wochenübersicht")

for tag in woche:
    with st.expander(f"{tag.strftime('%A, %d.%m.%Y')} – {get_zyklusphase(tag, zyklus_start, zyklus_länge)}"):
        st.subheader("Essensplanung")
        st.text_area(f"Essen geplant ({tag})", key=f"essen_geplant_{tag}")
        st.text_area(f"Essen gegessen ({tag})", key=f"essen_ist_{tag}")
        
        st.subheader("Sport")
        st.text_input(f"Sport geplant ({tag})", key=f"sport_geplant_{tag}")
        st.text_input(f"Sport gemacht ({tag})", key=f"sport_ist_{tag}")
        
        st.subheader("Vitamine")
        for v in st.session_state.vitamine:
            st.checkbox(f"{v} genommen ({tag})", key=f"{v}_{tag}")

st.sidebar.header("Vitaminliste bearbeiten")
neues_vitamin = st.sidebar.text_input("Neues Vitamin hinzufügen")
if st.sidebar.button("Hinzufügen") and neues_vitamin:
    st.session_state.vitamine.append(neues_vitamin)

if st.sidebar.button("App zurücksetzen"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()
