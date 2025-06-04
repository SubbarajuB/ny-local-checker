import streamlit as st
import pandas as pd

# Load reference NY product lists
@st.cache_data
def load_ny_products():
    try:
        ny1 = pd.read_csv("NY_Grown_Certified.csv")
        ny2 = pd.read_csv("Small_Farms_Producers.csv")
        
        all_text = pd.concat([ny1, ny2], ignore_index=True).astype(str).apply(lambda x: x.str.lower())
        ny_keywords = set()
        for col in all_text.columns:
            ny_keywords.update(word for word in all_text[col].dropna().str.split().explode() if word)
        return ny_keywords
    except Exception as e:
        st.error(f"❌ Failed to load NY product list: {e}")
        return set()

ny_keywords = load_ny_products()

# --- UI ---
st.title("🗽 NY LOCAL Product Checker")
uploaded_file = st.file_uploader("📄 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
        st.write("✅ Detected columns:", df.columns.tolist())

        # Let user choose the column
        selected_column = st.selectbox("🔍 Select the column to check NY LOCAL match:", df.columns)

        def is_ny_match(text):
            if pd.isnull(text):
                return False
            words = str(text).lower().split()
            return any(word in ny_keywords for word in words)

        df['is_ny_local'] = df[selected_column].apply(is_ny_match)

        # Show stats
        ny_count = df['is_ny_local'].sum()
        total = len(df)
        percentage = (ny_count / total) * 100 if total else 0
        st.success(f"🟢 {ny_count} NY LOCAL items out of {total} ({percentage:.2f}%)")

        st.dataframe(df)

        # Allow download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="ny_local_result.csv", mime='text/csv')

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
