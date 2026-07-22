import pandas as pd
import streamlit as st

from utils.api_client import APIClientError, create_prediction

st.set_page_config(page_title="Batch Prediction", page_icon="📦")

st.title("📦 Batch Prediction")
st.write(
    "Upload a CSV with columns `credit_score`, `geography`, `gender`, `age`, "
    "`balance`, `is_active_member` to score multiple customers at once."
)

REQUIRED_COLUMNS = [
    "credit_score",
    "geography",
    "gender",
    "age",
    "balance",
    "is_active_member",
]

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        st.error(f"CSV is missing required columns: {', '.join(missing_cols)}")
    else:
        st.dataframe(df.head(), use_container_width=True, hide_index=True)

        if st.button("Run batch prediction", type="primary"):
            results = []
            progress = st.progress(0, text="Scoring customers...")

            # NOTE: there's no batch endpoint on the API yet, so each row is
            # sent as its own request. For large files this may be slow.
            for i, row in enumerate(df.to_dict(orient="records")):
                payload = {col: row[col] for col in REQUIRED_COLUMNS}
                try:
                    prediction = create_prediction(payload)
                    results.append({**payload, **prediction, "error": None})
                except APIClientError as e:
                    results.append({**payload, "error": str(e)})

                progress.progress((i + 1) / len(df), text=f"Scored {i + 1}/{len(df)}")

            progress.empty()
            results_df = pd.DataFrame(results)
            st.success(f"Finished scoring {len(df)} customers.")
            st.dataframe(results_df, use_container_width=True, hide_index=True)

            st.download_button(
                "Download results as CSV",
                data=results_df.to_csv(index=False).encode("utf-8"),
                file_name="batch_prediction_results.csv",
                mime="text/csv",
            )