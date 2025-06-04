import streamlit as st
import pandas as pd

# Reference NY LOCAL product CSVs
NY_FILES = ["NY Grown & Certified-Grid view.csv", "Small Farms and Producers-Grid 2 (1).csv"]

@st.cache_data
def load_ny_products():
    ny_set = set()
    for file in NY_FILES:
        try:
            df = pd.read_csv(file)
            for col in df.columns:
                df[col] = df[col].astype(str).str.lower().str.strip()
                ny_set.update(df[col].dropna())
        except Exception as e:
            st.warning(f"⚠️ Failed to load NY product list from `{file}`: {e}")
    return ny_set

# Streamlit UI
st.set_page_config(page_title="NY LOCAL Product Checker", layout="wide")
st.title("🌽 NY LOCAL Product Checker")
st.markdown("Upload your Excel sheet and select a column to match against the NY LOCAL product list.")

uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        # Read and clean the uploaded Excel file
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.replace(r"\s+", " ", regex=True).str.strip().str.lower()
        st.write("✅ Columns Detected:", df.columns.tolist())

        # Let user select a column to compare
        selected_col = st.selectbox("🔍 Choose a column to match with NY LOCAL products:", df.columns)

        # Load NY product names from both reference CSVs
        ny_products = load_ny_products()

        if not ny_products:
            st.error("❌ Could not load NY product data. Please check the CSV files.")
        else:
            # Partial match: check if any NY product word is in the selected cell
            df['is_ny_local'] = df[selected_col].astype(str).str.lower().apply(
                lambda x: any(ny_item in x for ny_item in ny_products)
            )

            # Stats
            ny_count = df['is_ny_local'].sum()
            total_count = len(df)
            percentage = (ny_count / total_count) * 100 if total_count else 0

            st.markdown(f"### ✅ Match Result:")
            st.success(f"🟢 Found {ny_count} NY LOCAL items out of {total_count} ({percentage:.2f}%)")
            st.dataframe(df)

            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Results", data=csv, file_name="ny_local_result.csv", mime='text/csv')

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
