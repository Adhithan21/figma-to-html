import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5000"

st.title("Figma to HTML & CSS Converter")

file_key = st.text_input("Enter Figma File Key")

if st.button("Fetch Figma JSON"):
    try:
        response = requests.post(f"{BACKEND_URL}/fetch-figma", json={"file_key": file_key}, timeout=20)
        response.raise_for_status()
        st.session_state["figma_json"] = response.json()["figma_json"]
        st.success("Figma JSON Fetched!")
        st.json(st.session_state["figma_json"])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching JSON: {e}")

if "figma_json" in st.session_state:
    if st.button("Convert to HTML & CSS"):
        try:
            response = requests.post(f"{BACKEND_URL}/convert-to-html", json={"file_key": file_key}, timeout=60)
            response.raise_for_status()
            html_css_code = response.json()["html_css_code"]
            st.success("Conversion Successful!")
            st.code(html_css_code, language="html")
        except requests.exceptions.RequestException as e:
            st.error(f"Error converting JSON: {e}")
