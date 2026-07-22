import streamlit as st

from utils.api_client import APIClientError, health_check, list_predictions

st.set_page_config(
    page_title="Bank Churn Predictor",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 Bank Churn Prediction Dashboard")

st.markdown(
    """
    Welcome! This app talks to the churn prediction API to score customers,
    review past predictions, and record real-world outcomes.

    Use the sidebar to navigate:

    - **Single Prediction** — score one customer manually
    - **Batch Prediction** — upload a CSV and score many customers at once
    - **Fetch & Update Actuals** — record the true outcome for a past prediction
    - **Paginated Data** — browse all stored predictions
    """
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("API status")
    try:
        health_check()
        st.success("API is reachable ✅")
    except APIClientError as e:
        st.error(f"API unreachable: {e}")

with col2:
    st.subheader("Recent predictions")
    try:
        result = list_predictions(page=1, limit=5)
        data = result.get("data", [])
        if data:
            st.dataframe(data, use_container_width=True, hide_index=True)
        else:
            st.info("No predictions recorded yet.")
    except APIClientError as e:
        st.warning(f"Couldn't load recent predictions: {e}")