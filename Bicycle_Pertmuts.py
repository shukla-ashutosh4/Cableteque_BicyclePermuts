"""
streamlit_bicycle_generator.py

Simple Streamlit app that reads a Bicycle-style Excel file and generates
all permutations as JSON / CSV. Sidebar is collapsed by default for a cleaner view.
"""

from typing import Dict, List
import streamlit as st
import pandas as pd
import itertools
import json
import io

# Page config: sidebar collapsed initially
st.set_page_config(page_title="Bicycle Generator", layout="wide", initial_sidebar_state="collapsed")

# ---------------------- Core generator logic ----------------------

def generate_bicycles_from_sheets(sheets: Dict[str, pd.DataFrame], id_separator: str = "-", precedence: str = "designator_order") -> List[Dict[str, str]]:
    """
    Generate bicycle permutations from a dict of pandas DataFrames.

    sheets: dict mapping sheet_name -> DataFrame (as from pd.read_excel(..., sheet_name=None))
    id_separator: string placed between ID parts when building the ID
    precedence: 'designator_order' or 'sheet_priority'
    """
    if "ID" not in sheets:
        raise ValueError("Excel file must contain a sheet named 'ID'")

    # ID sheet and designators
    id_df = sheets["ID"].astype(object)
    designator_names = list(id_df.columns)

    lists_of_values = []
    for col in designator_names:
        vals = [str(v) for v in id_df[col].tolist() if pd.notna(v)]
        lists_of_values.append(vals)

    # GENERAL sheet -> apply to every bike
    general = {}
    if "GENERAL" in sheets:
        gen_df = sheets["GENERAL"].astype(object)
        if gen_df.shape[0] >= 1:
            row = gen_df.iloc[0]
            for k, v in row.items():
                if pd.notna(v):
                    general[str(k)] = str(v)

    # Other sheets: map first-column-header -> DataFrame
    designator_sheet_map: Dict[str, pd.DataFrame] = {}
    for sheet_name, df in sheets.items():
        if sheet_name in ("ID", "GENERAL"):
            continue
        if df.shape[1] < 1:
            continue
        first_col_name = df.columns[0]
        designator_sheet_map[first_col_name] = df.astype(object)

    # If any designator has no values -> return empty
    if any(len(vals) == 0 for vals in lists_of_values):
        return []

    combos = list(itertools.product(*lists_of_values))
    bicycles: List[Dict[str, str]] = []

    # Determine sheet application order
    if precedence == "designator_order":
        sheet_application_order = ("designator_order", designator_names)
    else:
        sheet_application_order = ("sheet_priority", list(designator_sheet_map.keys()))

    for combo in combos:
        parts = [str(p) for p in combo]
        bike_id = id_separator.join(parts)
        bike: Dict[str, str] = {"ID": bike_id}
        bike.update(general)

        if sheet_application_order[0] == "designator_order":
            for i, designator_value in enumerate(combo):
                designator_name = designator_names[i]
                if designator_name not in designator_sheet_map:
                    continue
                df = designator_sheet_map[designator_name]
                first_col = df.columns[0]
                mask = df[first_col].astype(str) == str(designator_value)
                matched = df[mask]
                if matched.shape[0] == 0:
                    continue
                for _, row in matched.iterrows():
                    for col in df.columns[1:]:
                        val = row[col]
                        if pd.isna(val):
                            continue
                        bike[str(col)] = str(val)
        else:
            for sheet_designator_name in sheet_application_order[1]:
                if sheet_designator_name not in designator_names:
                    continue
                idx = designator_names.index(sheet_designator_name)
                chosen_value = combo[idx]
                df = designator_sheet_map[sheet_designator_name]
                first_col = df.columns[0]
                mask = df[first_col].astype(str) == str(chosen_value)
                matched = df[mask]
                if matched.shape[0] == 0:
                    continue
                for _, row in matched.iterrows():
                    for col in df.columns[1:]:
                        val = row[col]
                        if pd.isna(val):
                            continue
                        bike[str(col)] = str(val)

        bicycles.append(bike)

    return bicycles

# ---------------------- Streamlit UI ----------------------

# Sidebar controls
st.sidebar.header("Options")
id_separator = st.sidebar.text_input("ID separator", value="-")
precedence = st.sidebar.selectbox(
    "Conflict resolution (which source can override)",
    options=["designator_order", "sheet_priority"],
    index=0,
    format_func=lambda x: "Designator order (ID columns)" if x == "designator_order" else "Sheet priority (sheet order)"
)
show_preview = st.sidebar.checkbox("Show preview table", value=True)
preview_rows = st.sidebar.number_input("Preview rows", min_value=5, max_value=10000, value=50, step=5)

st.sidebar.markdown("---")
st.sidebar.markdown("**Theme colors**")
primary_color = st.sidebar.color_picker("Primary / accent color", value="#0A84FF")
background_color = st.sidebar.color_picker("Background color", value="#FFFFFF")
card_color = st.sidebar.color_picker("Card background color", value="#F8F9FB")

# Inject CSS theme using chosen colors
st.markdown(f"""
<style>
    .stApp {{
        background: {background_color};
    }}
    .card {{
        background: {card_color};
        padding: 12px;
        border-radius: 10px;
    }}
    .accent {{
        color: {primary_color};
    }}
    /* Make download buttons slightly nicer */
    button[title="Download data"] {{
        border-radius: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# Main UI
st.title("🚲 Bicycle Generator")
st.markdown("Upload an Excel file (.xlsx) that matches the `Bicycle.xlsx` structure (ID, GENERAL, other sheets). The app will generate every bike permutation and let you download the JSON/CSV.")

uploaded_file = st.file_uploader("Choose Bicycle .xlsx file", type=["xlsx"])

if uploaded_file is not None:
    try:
        with st.spinner("Reading Excel file..."):
            xls_sheets = pd.read_excel(uploaded_file, sheet_name=None, dtype=str, engine="openpyxl")

        st.success(f"Read sheets: {', '.join(list(xls_sheets.keys()))}")

        with st.spinner("Generating permutations..."):
            bicycles = generate_bicycles_from_sheets(xls_sheets, id_separator=id_separator, precedence=precedence)

        st.markdown(f"**{len(bicycles)} permutations generated**")

        if len(bicycles) == 0:
            st.warning("No permutations generated. Ensure each ID column has at least one value.")
        else:
            if show_preview:
                df_preview = pd.DataFrame(bicycles)
                st.markdown("## Preview")
                st.dataframe(df_preview.head(preview_rows))

            st.markdown("---")
            st.markdown("### Quick find")
            df_all = pd.DataFrame(bicycles)
            all_fields = list(df_all.columns)
            chosen_field = st.selectbox("Field to filter by", options=all_fields, index=0)
            unique_vals = sorted(df_all[chosen_field].dropna().unique().tolist())
            chosen_val = st.selectbox("Value", options=["(any)"] + unique_vals)
            if chosen_val != "(any)":
                filtered = df_all[df_all[chosen_field] == chosen_val]
            else:
                filtered = df_all
            st.markdown(f"Showing {filtered.shape[0]} rows matching filter")
            st.dataframe(filtered.head(200))

            json_bytes = json.dumps(bicycles, ensure_ascii=False, indent=4).encode("utf-8")
            st.download_button(label="Download JSON", data=json_bytes, file_name="bicycles.json", mime="application/json")

            csv_bytes = df_all.to_csv(index=False).encode("utf-8")
            st.download_button(label="Download CSV", data=csv_bytes, file_name="bicycles.csv", mime="text/csv")

            st.markdown("---")
            st.markdown("### Inspect single bike")
            ids = df_all["ID"].tolist()
            id_choice = st.selectbox("Choose ID", options=ids)
            bike_obj = df_all[df_all["ID"] == id_choice].iloc[0].to_dict()
            st.json(bike_obj)

    except Exception as e:
        st.error(f"Error processing file: {e}")

# Footer / credits
st.markdown("---")
st.markdown("**Special thanks to the Cableteque team for inspiration and support.**")

# Replace this with your LinkedIn profile URL
LINKEDIN_URL = "https://www.linkedin.com/in/your-linkedin-profile"
st.markdown(f"LinkedIn: {LINKEDIN_URL}")

# End of file
