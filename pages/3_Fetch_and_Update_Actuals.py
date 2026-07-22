import streamlit as st

from utils.api_client import APIClientError, update_actual

st.set_page_config(page_title="Fetch & Update Actuals", page_icon="📝")

st.title("📝 Fetch & Update Actuals")
st.write("Record the real-world churn outcome for a previously scored customer.")

with st.form("update_actual_form"):
    prediction_id = st.text_input("Prediction ID (UUID)")
    actual_churn = st.selectbox("Did the customer actually churn?", ["Yes", "No"])
    notes = st.text_area(
        "Notes (optional)", placeholder="e.g. prediction was wrong, too high confidence"
    )

    submitted = st.form_submit_button("Update actual outcome", type="primary")

if submitted:
    if not prediction_id.strip():
        st.warning("Please enter a prediction ID.")
    else:
        with st.spinner("Updating record..."):
            try:
                result = update_actual(
                    prediction_id=prediction_id.strip(),
                    actual_churn=1 if actual_churn == "Yes" else 0,
                    notes=notes.strip() or None,
                )
            except APIClientError as e:
                if e.status_code == 404:
                    st.error(f"No prediction found with ID `{prediction_id}`.")
                else:
                    st.error(f"Update failed: {e}")
            else:
                st.success("Prediction updated successfully.")
                st.json(result)