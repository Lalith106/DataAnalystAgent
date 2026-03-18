import streamlit as st
import pandas as pd
from agent.graph import graph
from data.dataset_store import set_df, clear_df


st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
)

st.markdown("""
<style>

/* 🌤️ Light Blue Background */
.stApp {
    background: linear-gradient(135deg, #e0f2fe, #bae6fd);
}

/* 🧠 Main text */
.block-container {
    color: #0f172a;
}

/* 📊 Headers */
h1, h2, h3 {
    color: #0c4a6e;
}

/* 📂 Upload label */
[data-testid="stFileUploader"] label {
    color: #0c4a6e !important;
    font-weight: 600;
}

/* Upload box inner text */
[data-testid="stFileUploader"] section {
    color: #1e293b !important;
}

/* Uploaded filename */
[data-testid="stFileUploader"] small {
    color: #0369a1 !important;
}

/* 📊 Dataframe (clean white card) */
[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 12px;
    padding: 8px;
}

/* 💬 Chat messages */
[data-testid="stChatMessage"] {
    background-color: rgba(255,255,255,0.7);
    color: #0f172a !important;
    border-radius: 10px;
    padding: 10px;
}

/* ✏️ Chat input */
[data-testid="stChatInput"] textarea {
    background-color: white !important;
    color: #0f172a !important;
    border-radius: 10px;
}

/* 🔘 Buttons */
button {
    background-color: #38bdf8 !important;
    color: #0f172a !important;
    border-radius: 8px;
    font-weight: 600;
}

/* 📄 Paragraph text */
p, li {
    color: #1e293b !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='
padding:20px;
border-radius:12px;
background: rgba(255,255,255,0.6);
backdrop-filter: blur(8px);
text-align:center;
margin-bottom:20px;
'>
<h1># 📊 AI Data Analyst 🤖</h1>
<p>Upload data • Analyze • Discover insights 💡</p>
</div>
""", unsafe_allow_html=True)



if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

def data_quality_report(df):
    st.markdown("### 📊 Data Quality Report")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📋 Rows", len(df))

    with col2:
        st.metric("📊 Columns", len(df.columns))

    with col3:
        st.metric("❗ Missing Values", df.isnull().sum().sum())

    # Column-wise nulls
    st.markdown("#### 🧹 Missing Values by Column")
    nulls = df.isnull().sum().reset_index()
    nulls.columns = ["Column", "Missing Values"]
    st.dataframe(nulls)

    # Duplicate rows
    st.markdown("#### 🔁 Duplicate Rows")
    st.write(df.duplicated().sum())

def load_file(uploaded_file):
    try:
        filename = uploaded_file.name.lower()

        # ---------- CSV ----------
        if filename.endswith(".csv"):
            try:
                df = pd.read_csv(uploaded_file)
            except:
                df = pd.read_csv(
                    uploaded_file,
                    encoding="latin1",
                    on_bad_lines="skip",
                    engine="python"
                )

        # ---------- Excel ----------
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)

        # ---------- Parquet ----------
        elif filename.endswith(".parquet"):
            df = pd.read_parquet(uploaded_file)

        else:
            raise Exception("Unsupported file type")

        # ---------- Fix column names only ----------
        df.columns = df.columns.astype(str).str.strip()

        return df

    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        return None
    
uploaded_file = st.file_uploader("Upload your dataset", type=["csv","xlsx","parquet"])

if uploaded_file is not None:
    df = load_file(uploaded_file)

    if df is not None:
        st.success("✅ File loaded successfully")
        st.session_state.file_uploaded = True
        set_df(df)
        st.markdown("### 📄 Dataset Preview")
        st.dataframe(df.head())
        data_quality_report(df)

question = st.chat_input("💬 Ask Questions About Your Data")

if question and st.session_state.file_uploaded:
    result = graph.invoke({"question": question})
    answer = result["result"]

    # Save to history
    st.session_state.chat_history.append({
        "question": question,
        "answer": answer
    })

for chat in st.session_state.chat_history:

    with st.chat_message("user"):
        st.write(chat["question"])

    with st.chat_message("assistant"):
        st.write(chat["answer"])


# -------- Clear Button --------

if st.button("Clear Chat"):

    st.session_state.chat_history = []
    st.session_state.file_uploaded = False

    clear_df()

    st.rerun()