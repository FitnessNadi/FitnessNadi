import streamlit as st
import pandas as pd
import datetime
import os
import re

st.set_page_config(layout="wide")
st.title("Vegane Gesundheits‑App: Planung, Tracking & Nährstoffanalyse")

DATA_FILE = "tagebuch.csv"
NUTRI_FILE = "vegan_naehrstoffe.csv"
REFERENZ = {
    "Eisen_mg": 15,
    "Magnesium_mg": 300,
    "Kalzium_mg": 1000,
    "Zink_mg": 8,
    "Protein_g": 50,
}

# ====== load nutrient table =====
nutri_df = pd.read_csv(NUTRI_FILE)
nutri_df['Lebensmittel_lower'] = nutri_df['Lebensmittel'].str.lower()

# ===== session defaults =====
if "vitamine" not in st.session_state:
    st.session_state.vitamine = ["B12", "Vitamin D", "Magnesium"]
if "zyklus_start" not in st.session_state:
    st.session_state.zyklus_start = datetime.date.today()
if "zyklus_länge" not in st.session_state:
    st.session_state.zyklus_länge = 28

# ===== helper =====
def zyklusphase(datum, start, länge):
    delta = (datum - start).days % länge
    if delta < 5:
        return "Periode"
    elif 5 <= delta < 13:
        return "Follikelphase"
    elif 13 <= delta < 16:
        return "Eisprung"
    else:
        return "Lutealphase"

def parse_food(text):
    """Return nutrient totals based on foods recognised in text (lowercased)."""
    totals = {k: 0.0 for k in REFERENZ}
    found = []
    lower = text.lower()
    for _, row in nutri_df.iterrows():
        if row['Lebensmittel_lower'] in lower:
            found.append(row['Lebensmittel'])
            for k in totals:
                totals[k] += row[k]
    return totals, found

# ===== storage load =====
base_cols = ["Datum", "Essen geplant", "Essen gegessen", "Sport geplant", "Sport gemacht"]
nutrient_cols = list(REFERENZ.keys())
vitamin_cols = st.session_state.vitamine

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, parse_dates=['Datum'])
else:
    df = pd.DataFrame(columns=base_cols + nutrient_cols + vitamin_cols)

# ===== sidebar settings =====
st.sidebar.header("Zyklus")
st.sidebar.date_input("Erster Tag der letzten Periode", value=st.session_state.zyklus_start, key="zyklus_start")
st.sidebar.number_input("Zykluslänge (Tage)", 20, 40, value=st.session_state.zyklus_länge, key="zyklus_länge")

st.sidebar.header("Vitamine verwalten")
new_vit = st.sidebar.text_input("Neues Vitamin")
if st.sidebar.button("Hinzufügen") and new_vit:
    if new_vit not in st.session_state.vitamine:
        st.session_state.vitamine.append(new_vit)
        st.experimental_rerun()

# ===== main planner =====
today = datetime.date.today()
week = [today + datetime.timedelta(days=i) for i in range(7)]
st.header("Wochenplan & Nährstoffbilanz")
for d in week:
    row = df[df['Datum'] == pd.Timestamp(d)]
    row_data = row.iloc[0] if not row.empty else {}
    with st.expander(f"{d.strftime('%A %d.%m.%Y')} – {zyklusphase(d, st.session_state.zyklus_start, st.session_state.zyklus_länge)}"):
        planned = st.text_area("Essen geplant", row_data.get("Essen geplant",""), key=f"plan_{d}")
        eaten = st.text_area("Essen gegessen", row_data.get("Essen gegessen",""), key=f"eat_{d}")
        sport_p = st.text_input("Sport geplant", row_data.get("Sport geplant",""), key=f"sportp_{d}")
        sport_a = st.text_input("Sport gemacht", row_data.get("Sport gemacht",""), key=f"sporta_{d}")

        vit_results = {}
        for idx, v in enumerate(st.session_state.vitamine):
            key_cb = f"{v}_{d}_{idx}"
            default_val = row_data.get(v,"nein") == "ja"
            vit_results[v] = st.checkbox(f"{v} genommen", value=default_val, key=key_cb)

        # nutrient calc on eaten field
        totals, found_foods = parse_food(eaten)
        st.markdown("**Erkannte Lebensmittel (Auswertung):** " + (', '.join(found_foods) if found_foods else "–"))
        st.subheader("Tägliche Nährstoffbilanz (aus gegessen)")
        for k, val in totals.items():
            target = REFERENZ[k]
            pct = int(round(val/target*100))
            status = "✅" if pct >= 100 else ("⚠️" if pct >=70 else "❌")
            st.write(f"{status} {k.replace('_mg','').replace('_g','')} : {val:.1f} / {target} ({pct} %)")

        if st.button(f"Speichern {d}", key=f"save_{d}"):
            new_row = {
                "Datum": pd.Timestamp(d),
                "Essen geplant": planned,
                "Essen gegessen": eaten,
                "Sport geplant": sport_p,
                "Sport gemacht": sport_a,
            }
            # nutrients
            new_row.update(totals)
            # vitamins
            for v in st.session_state.vitamine:
                new_row[v] = "ja" if vit_results[v] else "nein"
            # update DF
            df = df[df["Datum"] != pd.Timestamp(d)]
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Gespeichert!")

# ===== overview stats =====
if not df.empty:
    st.header("Wöchentliche Nährstoff-Übersicht")
    last7 = df[df["Datum"] >= pd.Timestamp(today - datetime.timedelta(days=6))]
    summary = last7[nutrient_cols].sum()
    cols = st.columns(len(summary))
    for i, (k,val) in enumerate(summary.items()):
        target_total = REFERENZ[k]*7
        pct = int(round(val/target_total*100))
        status = "✅" if pct >= 100 else ("⚠️" if pct >=70 else "❌")
        cols[i].metric(k.replace('_mg','').replace('_g',''), f"{val:.0f} / {target_total}", f"{pct}% {status}")
