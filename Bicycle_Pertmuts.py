"""
Streamlit Bicycle Generator

Run this app with:
    pip install streamlit pandas openpyxl
    streamlit run streamlit_bicycle_generator.py

What it does
- Lets users upload an Excel (.xlsx) file following the Bicycle.xlsx format
  described earlier (ID sheet, GENERAL sheet, other sheets with first
  column == designator name).
- Generates all bicycle permutations and shows a preview.
- Provides options for ID separator, conflict-resolution strategy, and
  simple theme color customisation.
- Lets users download the resulting JSON file.

Design and teaching notes are included in the user-facing UI and in the
comments below.
"""

from typing import Dict, List
import streamlit as st
import pandas as pd
import itertools
import json
import io


st.set_page_config(page_title="Bicycle Generator", layout="wide")

# ---------------------- Core generator logic ----------------------

def generate_bicycles_from_sheets(sheets: Dict[str, pd.DataFrame], id_separator: str = "", precedence: str = "designator_order") -> List[Dict[str, str]]:
    """Generate bicycle permutations from a dict of pandas DataFrames.

    Parameters
    - sheets: mapping sheet_name -> DataFrame as returned by pandas.read_excel(..., sheet_name=None)
    - id_separator: string placed between ID designators when building the ID
    - precedence: controls field override behavior. Options:
        - 'designator_order': apply designator sheets in the order of columns in the ID sheet (default)
        - 'sheet_priority': apply sheets in the order they appear (alphabetical by sheet name) so their fields override GENERAL

    Returns a list of dictionary objects representing bicycles.
    """
    # 1. ID sheet
    if "ID" not in sheets:
        raise ValueError("Excel file must contain a sheet named 'ID'")
    id_df = sheets["ID"].astype(object)
    designator_names = list(id_df.columns)

    # Build value lists for each designator column (skip blanks)
    lists_of_values = []
    for col in designator_names:
        vals = [str(v) for v in id_df[col].tolist() if pd.notna(v)]
        lists_of_values.append(vals)

    # 2. GENERAL sheet
    general = {}
    if "GENERAL" in sheets:
        gen_df = sheets["GENERAL"].astype(object)
        if gen_df.shape[0] >= 1:
            row = gen_df.iloc[0]
            for k, v in row.items():
                if pd.notna(v):
                    general[str(k)] = str(v)

    # 3. designator sheets: map first-column-header -> DataFrame
    designator_sheet_map: Dict[str, pd.DataFrame] = {}
    # Keep original insertion order to support 'sheet_priority' option
    for sheet_name, df in sheets.items():
        if sheet_name in ("ID", "GENERAL"):
            continue
        if df.shape[1] < 1:
            continue
        first_col_name = df.columns[0]
        designator_sheet_map[first_col_name] = df.astype(object)

    # Guard: if any designator list empty -> no permutations
    if any(len(vals) == 0 for vals in lists_of_values):
        return []

    # Generate cartesian product
    combos = list(itertools.product(*lists_of_values))

    bicycles = []
    # Precompute the sheet application order based on precedence
    if precedence == 'designator_order':
        # For each designator, we'll look up matching sheet by the designator name
        sheet_application_order = ('designator_order', designator_names)
    else:
        # sheet_priority: apply sheets in the order they appear in the Excel file
        sheet_application_order = ('sheet_priority', list(designator_sheet_map.keys()))

    for combo in combos:
        # Build ID
        parts = [str(p) for p in combo]
        bike_id = id_separator.join(parts)
        bike: Dict[str, str] = {"ID": bike_id}

        # Start with GENERAL fields
        bike.update(general)

        # Apply fields depending on precedence mode
        if sheet_application_order[0] == 'designator_order':
            # For each designator in ID order, if there is a sheet with the same name,
            # apply rows that match the chosen designator value
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
            # sheet_priority: apply sheets in the order of designator_sheet_map keys
            # For each sheet, look up rows matching the value for that designator position
            # Find the index of the designator in the ID columns (if present)
            for sheet_designator_name in sheet_application_order[1]:
                if sheet_designator_name not in designator_names:
                    # if the designator from the sheet is not present in the ID sheet, skip
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

# Sidebar: options and theme
st.sidebar.header("Options")
id_separator = st.sidebar.text_input("ID separator", value="-")
precedence = st.sidebar.selectbox("Conflict resolution (which source can override)", options=["designator_order", "sheet_priority"], index=0, format_func=lambda x: "Designator order (ID columns)" if x=="designator_order" else "Sheet priority (sheet order)")
show_preview = st.sidebar.checkbox("Show preview table", value=True)
preview_rows = st.sidebar.number_input("Preview rows", min_value=5, max_value=500, value=50, step=5)

st.sidebar.markdown("---")
st.sidebar.markdown("**Theme colors**")
primary_color = st.sidebar.color_picker("Primary / accent color", value="#0A84FF")
background_color = st.sidebar.color_picker("Background color", value="#FFFFFF")
card_color = st.sidebar.color_picker("Card background color", value="#F8F9FB")

st.sidebar.markdown("---")
st.sidebar.markdown("Need a sample .xlsx that follows the format? Use the button below to download an example.")

# Create a downloadable sample Excel crafted in memory
if st.sidebar.button("Download example Bicycle.xlsx"):
    sample_buffer = io.BytesIO()
    # Build a tiny sample workbook with pandas
    id_df = pd.DataFrame({
        'Model number': ['CITY', 'CITY'],
        'Brakes': ['R', 'D'],
        'Wheels': ['26', '27'],
        'Frame size': ['16', '18'],
        'Groupset': ['Acera', 'Tourney'],
        'Suspension': ['FALSE', 'TRUE'],
        'Color': ['RED', 'CYAN']
    })
    general_df = pd.DataFrame({
        'Manufacturer': ['Bikes INC'],
        'Type': ['City']
    })
    a_df = pd.DataFrame({'Color': ['RED', 'CYAN'], 'Frame color': ['RED', 'CYAN'], 'Logo': ['TRUE', 'FALSE']})
    # write
    with pd.ExcelWriter(sample_buffer, engine='openpyxl') as writer:
        id_df.to_excel(writer, sheet_name='ID', index=False)
        general_df.to_excel(writer, sheet_name='GENERAL', index=False)
        a_df_correct = a_df.copy()
        a_df_correct.insert(0, 'Color', ['RED', 'CYAN'])
        a_df_correct.to_excel(writer, sheet_name='Color', index=False)
    sample_buffer.seek(0)
    st.sidebar.download_button(label='Download example .xlsx', data=sample_buffer, file_name='Bicycle_example.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Inject a small CSS theme using the chosen colors
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
</style>
""", unsafe_allow_html=True)

# Main area
st.title("🚲 Bicycle Generator")
st.markdown("Upload an Excel file (.xlsx) that matches the `Bicycle.xlsx` structure (ID, GENERAL, other sheets). The app will generate every bike permutation and let you download the JSON.")

uploaded_file = st.file_uploader("Choose Bicycle .xlsx file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # read all sheets into DataFrames
        with st.spinner('Reading Excel file...'):
            xls_sheets = pd.read_excel(uploaded_file, sheet_name=None, dtype=str, engine='openpyxl')

        st.success(f"Read sheets: {', '.join(list(xls_sheets.keys()))}")

        # Generate bicycles
        with st.spinner('Generating permutations...'):
            bicycles = generate_bicycles_from_sheets(xls_sheets, id_separator=id_separator, precedence=precedence)

        st.markdown(f"**{len(bicycles)} permutations generated**")

        if len(bicycles) == 0:
            st.warning("No permutations generated. Check that every designator column in the ID sheet has at least one value.")
        else:
            # Show preview
            if show_preview:
                df_preview = pd.DataFrame(bicycles)
                st.markdown("## Preview")
                st.dataframe(df_preview.head(preview_rows))

            # Filters - allow user to filter by a field quickly
            st.markdown("---")
            st.markdown("### Quick find")
            df_all = pd.DataFrame(bicycles)
            all_fields = list(df_all.columns)
            chosen_field = st.selectbox("Field to filter by", options=all_fields, index=0)
            unique_vals = sorted(df_all[chosen_field].dropna().unique().tolist())
            chosen_val = st.selectbox("Value", options=['(any)'] + unique_vals)
            if chosen_val != '(any)':
                filtered = df_all[df_all[chosen_field] == chosen_val]
            else:
                filtered = df_all
            st.markdown(f"Showing {filtered.shape[0]} rows matching filter")
            st.dataframe(filtered.head(200))

            # Prepare JSON for download
            json_bytes = json.dumps(bicycles, ensure_ascii=False, indent=4).encode('utf-8')
            st.download_button(label='Download JSON', data=json_bytes, file_name='bicycles.json', mime='application/json')

            # Also let user download CSV (wide table)
            csv_bytes = df_all.to_csv(index=False).encode('utf-8')
            st.download_button(label='Download CSV', data=csv_bytes, file_name='bicycles.csv', mime='text/csv')

            # Show a single selected bike (by ID)
            st.markdown('---')
            st.markdown('### Inspect single bike')
            ids = df_all['ID'].tolist()
            id_choice = st.selectbox('Choose ID', options=ids)
            bike_obj = df_all[df_all['ID'] == id_choice].iloc[0].to_dict()
            st.json(bike_obj)

    except Exception as e:
        st.error(f"Error processing file: {e}")

else:
    st.info("Upload a Bicycle.xlsx file to begin. Use the sample file in the sidebar if you need a template.")

# ---------------------- Footer / teaching ----------------------
st.markdown("---")
with st.expander("How this works (short) "):
    st.markdown(
        """
**Overview**

1. `ID` sheet: each column is a *designator*. Each row value under that column is a possible value for that designator. The app builds every combination by taking one value from each column.
2. `GENERAL` sheet: row 1 values are applied to every bike.
3. Other sheets: the **first column header** is the designator name. Rows map a designator value (first-col cell) to a set of fields (other columns) to apply to bikes that use that designator value.

**ID building**: the app concatenates chosen designator values using the `ID separator` chosen in the sidebar. This improves readability (e.g. `CITY-R-26-16-Acera-FALSE-RED`).

**Conflict resolution**: if multiple sheets specify the same field for a bike, use the `conflict resolution` option to choose whether designator order or sheet priority determines which value wins.

"""
    )

with st.expander("Teach me more — deep dive"):
    st.markdown(
        """
**Implementation notes**

- We read the whole workbook into `sheets: Dict[str, DataFrame]` using `pandas.read_excel(..., sheet_name=None)`.
- The generator function constructs `combos = itertools.product(*lists_of_values)` — that is the cartesian product of designator values.
- For each combo, we build the ID string (`id_separator.join(parts)`) and copy GENERAL fields.
- Then we apply additional fields from matching rows in designator sheets. The app allows two override strategies: *designator order* (apply fields in order of ID columns) or *sheet priority* (apply fields in the order the sheets were discovered).

**Scalability**
- Cartesian products can explode. In your file you produced 5508 permutations. Keep an eye on the number of values per designator — multiply them and that is how many permutations you'll get.
- If users upload very large inputs, consider streaming processing or limiting allowed combinations.

**Security & privacy**
- The app runs locally by default when you run `streamlit run`. Files are processed in memory and not uploaded anywhere unless you deploy the app to a public host.
- If you deploy to a shared server, consider adding authentication and disk quotas, and be careful about storing uploaded files.

**Next steps / improvements**
- Add validation UI to show missing/ malformed sheets before generation.
- Add a dry-run mode that only lists the expected number of permutations (no field merging) for a quick sanity check.
- Add templating for ID format (e.g., allowing fixed prefixes/suffixes, zero-padding numbers, etc.).
- Expose logs and warnings about ambiguous or missing sheet mappings.

"""
    )

st.markdown("_If you'd like, I can adapt this app to deploy on Streamlit Cloud or package it into a Docker container. I can also add unit tests and CI integration — tell me which you'd prefer!_")
