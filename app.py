import streamlit as st
import pandas as pd

# === Configuration ===
NY_FILES = [
    "NY Grown & Certified-Grid view.csv",
    "Small Farms and Producers-Grid 2 (1).csv"
]

# === Load NY-local reference data ===
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

# === Streamlit App UI ===
st.set_page_config(page_title="NY LOCAL Product Checker", layout="wide")
st.title("🌽 NY LOCAL Product Checker")
st.markdown("Upload your Excel sheet and compare against NY Grown & Certified products.")

# === File Upload ===
uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.replace(r"\s+", " ", regex=True).str.strip().str.lower()
        st.write("✅ Columns Detected:", df.columns.tolist())

        # Column selector
        selected_col = st.selectbox("🔍 Choose column to check against NY products:", df.columns)

        # Load NY product references
        ny_products = load_ny_products()

        if not ny_products:
            st.error("❌ Could not load any NY product data. Check reference CSVs.")
        else:
            # Match logic ignoring nulls
            df['is_ny_local'] = df[selected_col].astype(str).str.lower().apply(
                lambda x: any(ny_item in x for ny_item in ny_products) if pd.notnull(x) else False
            )

            # Stats
            ny_count = df['is_ny_local'].sum()
            total_count = len(df)
            percent = (ny_count / total_count) * 100 if total_count else 0

            # Show result
            st.markdown(f"### ✅ Match Results")
            st.success(f"🟢 Found {ny_count} NY LOCAL items out of {total_count} ({percent:.2f}%)")
            st.dataframe(df)

            # Allow CSV download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Results", data=csv, file_name="ny_local_checked.csv", mime='text/csv')

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
