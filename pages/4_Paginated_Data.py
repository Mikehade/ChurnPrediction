import streamlit as st

from utils.api_client import APIClientError, list_predictions

st.set_page_config(page_title="Paginated Data", page_icon="📊", layout="wide")

st.title("📊 Paginated Data")
st.write("Browse all stored predictions.")

if "page" not in st.session_state:
    st.session_state.page = 1

col1, col2 = st.columns([1, 1])
with col1:
    st.number_input("Page", min_value=1, step=1, key="page")
with col2:
    limit = st.selectbox("Rows per page", [10, 25, 50, 100], index=2)

try:
    result = list_predictions(page=st.session_state.page, limit=int(limit))
except APIClientError as e:
    st.error(f"Could not load predictions: {e}")
else:
    data = result.get("data", [])

    if not data:
        st.info("No predictions on this page.")
    else:
        st.dataframe(data, use_container_width=True, hide_index=True)

    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        if st.session_state.page > 1 and st.button("⬅️ Previous page"):
            st.session_state.page -= 1
            st.rerun()
    with nav_col2:
        if len(data) == limit and st.button("Next page ➡️"):
            st.session_state.page += 1
            st.rerun()