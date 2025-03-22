import streamlit as st

from slit.app import initialize_state


def test_initialize_state():
    st.session_state.clear()

    initialize_state()

    assert "messages" in st.session_state
    assert st.session_state["messages"] == []

    assert "status" in st.session_state
    assert st.session_state["status"] == ""
