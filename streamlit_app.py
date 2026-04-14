import streamlit as st
import subprocess
import time
import requests
import os
import sys

st.set_page_config(page_title="Zomato API Backend", page_icon="🚀")

st.title("FastAPI Backend Wrapper")
st.write("This Streamlit app acts as a launcher for the true FastAPI backend on Streamlit Community Cloud.")

if 'fastapi_process' not in st.session_state:
    st.info("Starting FastAPI server via subprocess...")
    
    # Ensure the current directory is in PYTHONPATH so Phase2_BackendAPI can be resolved
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    # Run uvicorn on port 8000
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "Phase2_BackendAPI.main:app", "--host", "0.0.0.0", "--port", "8000"],
        env=env
    )
    st.session_state.fastapi_process = process
    
    # Wait for the server to spin up
    time.sleep(3)

st.success("FastAPI server should be running on the internal port 8000!")

st.markdown("### API Health Check")
try:
    # Try fetching from the locally running FastAPI
    response = requests.get("http://localhost:8000/api/metadata", timeout=5)
    if response.status_code == 200:
        st.success("✅ FastAPI is responding to requests!")
        st.json(response.json())
    else:
        st.warning(f"⚠️ FastAPI responded with status code: {response.status_code}")
except Exception as e:
    st.error(f"❌ Failed to reach FastAPI server: {e}")

st.markdown("""
---
> **Important Note:** While Streamlit Cloud handles this `streamlit_app.py` script on exposed ports (like 80/443 mapping to 8501), the internal port `8000` where FastAPI runs **might not be directly exposed to the Internet**. 
> 
> If your Next.js application on Vercel cannot reach `http://<your-streamlit-url>:8000`, Streamlit Community Cloud's infrastructure is blocking external access to secondary ports. In that case, you will need to pivot your backend deployment to **Render** or **Railway**.
""")
