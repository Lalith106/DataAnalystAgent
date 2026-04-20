import streamlit as st
import pandas as pd
from agent.graph import graph, generate_dataset_summary
from data.dataset_store import set_df, clear_df, generate_summary
import base64
import re


st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
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
    max-width: 100% !important;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
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

/* Make main app content span full width */
[data-testid="stAppViewContainer"] .main {
    max-width: 100% !important;
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


def safe_filename(text: str, default: str = "chart") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return slug[:60] if slug else default

def render_dataset_overview(df, dataset_summary_text: str):
    summary = generate_summary(df)

    st.markdown(
        """
        <div style='
            margin: 1rem 0 0.75rem 0;
            padding: 1rem 1.15rem;
            border-radius: 14px;
            background: rgba(255,255,255,0.88);
            border: 1px solid rgba(37,99,235,0.18);
            box-shadow: 0 6px 18px rgba(15,23,42,0.06);
        '>
            <h4 style='color:#0c4a6e; margin:0 0 0.35rem 0;'>🧠 AI-generated dataset summary</h4>
            <p style='color:#334155; margin:0;'>An overall summary built from dataset-level statistics, not just preview rows:</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(dataset_summary_text)

    st.markdown("#### 👀 Dataset Preview")
    st.dataframe(df.head(), use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div style='
            margin: 1rem 0 0.75rem 0;
            padding: 1.1rem 1.3rem;
            border-radius: 16px;
            background: rgba(255,255,255,0.84);
            border: 1px solid rgba(56,189,248,0.35);
            box-shadow: 0 8px 22px rgba(15,23,42,0.08);
        '>
            <h3 style='color:#0c4a6e; margin:0 0 0.35rem 0;'>🗂️ Dataset Overview</h3>
            <p style='color:#334155; margin:0;'>A unified snapshot of your dataset quality, structure, and key column insights.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Full-width KPI row
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("📋 Rows", f"{summary['rows']:,}")
    c2.metric("📊 Columns", summary["columns"])
    c3.metric("🔢 Numeric", len(summary["numeric_cols"]))
    c4.metric("🔤 Categorical", len(summary["categorical_cols"]))
    c5.metric("❗ Missing %", f"{summary['missing_pct']}%")
    c6.metric("🔁 Duplicates", f"{summary['duplicate_rows']:,}")

    # Full-width details area
    left, right = st.columns([1.15, 1.15], gap="large")

    with left:
        st.markdown("#### 🧹 Missing Values by Column")
        nulls = df.isnull().sum().reset_index()
        nulls.columns = ["Column", "Missing Values"]
        st.dataframe(nulls, use_container_width=True, hide_index=True)

        st.markdown("#### 🔢 Numeric Column Stats")
        if summary["numeric_stats"]:
            num_df = pd.DataFrame(summary["numeric_stats"]).rename(columns={
                "column": "Column", "min": "Min", "max": "Max",
                "mean": "Mean", "median": "Median", "std": "Std Dev", "nulls": "Nulls"
            })
            st.dataframe(num_df, use_container_width=True, hide_index=True)
        else:
            st.info("No numeric columns found.")

    with right:
        st.markdown("#### 🔤 Categorical Column Overview")
        if summary["cat_stats"]:
            cat_df = pd.DataFrame(summary["cat_stats"]).rename(columns={
                "column": "Column", "unique": "Unique Values",
                "top": "Most Frequent", "top_freq": "Freq", "nulls": "Nulls"
            })
            st.dataframe(cat_df, use_container_width=True, hide_index=True)
        else:
            st.info("No categorical columns found.")

        if summary["date_ranges"]:
            st.markdown("#### 📅 Date Columns")
            date_df = pd.DataFrame(summary["date_ranges"]).rename(columns={
                "column": "Column", "min": "Earliest", "max": "Latest"
            })
            st.dataframe(date_df, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div style='
            margin: 0.9rem 0 0.35rem 0;
            padding: 0.85rem 1rem;
            border-radius: 12px;
            background: rgba(56,189,248,0.12);
            border-left: 4px solid #38bdf8;
            color: #0c4a6e;
            font-weight: 600;
        '>
            👇 Now use the chat below to ask questions about your data!
        </div>
        """,
        unsafe_allow_html=True,
    )



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

        summary_cache_key = f"dataset_summary::{uploaded_file.name}"
        if st.session_state.get("dataset_summary_key") != summary_cache_key:
            try:
                st.session_state.dataset_summary_text = generate_dataset_summary(generate_summary(df))
            except Exception as e:
                st.session_state.dataset_summary_text = (
                    "The dataset appears to be a structured table with a mix of numeric and categorical fields. "
                    "Please review the preview below for the sample records and use the chat to explore the data further."
                )
                st.warning(f"⚠️ Could not generate AI summary: {e}")
            st.session_state.dataset_summary_key = summary_cache_key

        render_dataset_overview(df, st.session_state.dataset_summary_text)

question = st.chat_input("💬 Ask Questions About Your Data")

if question and st.session_state.file_uploaded:
    result = graph.invoke({"question": question})
    answer = result["result"]
    is_visualization = result.get("is_visualization", False)
    visualization_data = result.get("visualization_data", "")

    image_bytes = None
    if is_visualization and visualization_data:
        try:
            image_bytes = base64.b64decode(visualization_data)
        except Exception as e:
            print(f"[DEBUG] Failed to decode visualization image: {e}")

    download_name = f"{safe_filename(question)}.png"
    
    # Debug logging
    print(f"[DEBUG] is_visualization: {is_visualization}")
    print(f"[DEBUG] visualization_data length: {len(visualization_data) if visualization_data else 0}")
    print(f"[DEBUG] answer: {answer[:100] if answer else 'None'}")

    # Save to history
    st.session_state.chat_history.append({
        "question": question,
        "answer": answer,
        "is_visualization": is_visualization,
        "visualization_data": visualization_data,
        "visualization_bytes": image_bytes,
        "download_name": download_name,
    })

for idx, chat in enumerate(st.session_state.chat_history):

    with st.chat_message("user"):
        st.write(chat["question"])

    with st.chat_message("assistant"):
        is_viz = chat.get("is_visualization", False)
        viz_bytes = chat.get("visualization_bytes")
        download_name = chat.get("download_name", "chart.png")

        if is_viz and viz_bytes:
            try:
                st.markdown("#### 📊 Generated Visualization")
                st.image(viz_bytes, use_container_width=True, caption="Generated chart")
                st.download_button(
                    label="⬇️ Download chart as PNG",
                    data=viz_bytes,
                    file_name=download_name,
                    mime="image/png",
                    key=f"download_{idx}",
                )
            except Exception as e:
                st.warning(f"⚠️ Could not display image: {str(e)}")

            st.markdown(
                f"""
                <div style='\
                    margin-top: 0.75rem;\
                    padding: 0.9rem 1rem;\
                    border-radius: 12px;\
                    background: rgba(255,255,255,0.82);\
                    border: 1px solid rgba(56, 189, 248, 0.35);\
                    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);\
                    color: #0f172a;\
                '>
                    <strong style='color:#0c4a6e;'>Insight summary</strong><br>
                    {chat["answer"]}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.write(chat["answer"])


# -------- Clear Button --------

if st.button("Clear Chat"):

    st.session_state.chat_history = []
    st.session_state.file_uploaded = False

    clear_df()

    st.rerun()