import streamlit as st
import pandas as pd

# --- Load and clean NY product list ---
@st.cache_data
def load_ny_products(file_path):
    try:
        ny_df = pd.read_csv(file_path)
        ny_df.columns = ny_df.columns.str.strip().str.lower()
        st.write(f"✅ Columns in {file_path}:", ny_df.columns.tolist())

        for col in ny_df.columns:
            if 'product' in col or 'description' in col or 'item' in col:
                all_words = set()
                for item in ny_df[col].dropna():
                    words = str(item).lower().split()
                    all_words.update(words)
                return all_words

        raise ValueError("No suitable product column found.")
    except Exception as e:
        st.error(f"❌ Failed to load NY product list from {file_path}: {e}")
        return set()

# --- UI ---
st.title("🗽 NY LOCAL Product Checker (Fuzzy Matching)")
st.write("Upload your Excel/CSV product list. We'll check if any word in the item matches a NY-local product.")

# Load and merge NY product word sets
ny_words_1 = load_ny_products("NY Grown & Certified-Grid view.csv")
ny_words_2 = load_ny_products("Small Farms and Producers-Grid 2 (1).csv")
ny_word_set = ny_words_1.union(ny_words_2)

uploaded_file = st.file_uploader("📄 Upload your Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)

        df.columns = df.columns.str.strip().str.lower()
        st.write("✅ Cleaned columns in your file:", df.columns.tolist())

        possible_cols = ['item description', 'description', 'product name', 'product', 'item']
        matched_col = next((col for col in df.columns if col in possible_cols), None)

        if not matched_col:
            st.error("❌ Could not find a column for item descriptions. Expected one of: " + ", ".join(possible_cols))
        else:
            st.success(f"✅ Using column: '{matched_col}'")

            # Partial match logic: if ANY word from the item appears in ny_word_set
            def is_ny_local(item):
                words = str(item).lower().split()
                return any(word in ny_word_set for word in words)

            df['is_ny_local'] = df[matched_col].apply(is_ny_local)

            ny_count = df['is_ny_local'].sum()
            total = len(df)
            percent = (ny_count / total) * 100 if total else 0

            st.markdown("### 📊 NY Product Match Results")
            st.success(f"🟢 {ny_count} out of {total} items matched (One-word match, {percent:.2f}%)")

            st.dataframe(df)

            # Allow result download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Result CSV",
                data=csv,
                file_name="ny_local_fuzzy_checked.csv",
                mime='text/csv'
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
