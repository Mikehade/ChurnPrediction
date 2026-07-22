import streamlit as st

from utils.api_client import APIClientError, create_prediction

st.set_page_config(page_title="Single Prediction", page_icon="🔮")

st.title("🔮 Single Prediction")
st.write("Enter a customer's details to get a churn prediction.")

with st.form("single_prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        credit_score = st.number_input(
            "Credit score", min_value=300, max_value=900, value=650, step=1
        )
        geography = st.selectbox("Geography", ["France", "Germany", "Spain"])
        gender = st.selectbox("Gender", ["Male", "Female"])

    with col2:
        age = st.number_input("Age", min_value=18, max_value=100, value=35, step=1)
        balance = st.number_input(
            "Balance", min_value=0.0, value=50000.0, step=100.0, format="%.2f"
        )
        is_active_member = st.selectbox("Active member?", ["Yes", "No"])

    submitted = st.form_submit_button("Predict", type="primary")

if submitted:
    payload = {
        "credit_score": int(credit_score),
        "geography": geography,
        "gender": gender,
        "age": int(age),
        "balance": float(balance),
        "is_active_member": 1 if is_active_member == "Yes" else 0,
    }

    with st.spinner("Scoring customer..."):
        try:
            result = create_prediction(payload)
        except APIClientError as e:
            st.error(f"Prediction failed: {e}")
        else:
            churn_prob = result.get("churn_probability", 0.0)
            predicted = result.get("predicted_churn")

            st.divider()
            if predicted:
                st.error(f"⚠️ Predicted to churn — probability: {churn_prob:.0%}")
            else:
                st.success(f"✅ Predicted to stay — churn probability: {churn_prob:.0%}")

            st.metric("Decision threshold", result.get("decision_threshold"))
            st.caption(
                f"Model: {result.get('model_name')} (v{result.get('model_version')})"
            )