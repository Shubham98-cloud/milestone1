import streamlit as st
import subprocess
import time
import requests
import sys
import os
from pyngrok import ngrok

st.set_page_config(page_title="Zomato API Tunneled Backend", page_icon="🔗")

st.title("Zomato API Tunneled Backend")
st.write("This Streamlit app launches the FastAPI backend and uses Ngrok to tunnel it to the internet so your Next.js application can access it.")

# Authenticate Ngrok if provided in secrets/environment
ngrok_auth = os.environ.get("NGROK_AUTHTOKEN")
if ngrok_auth:
    try:
        ngrok.set_auth_token(ngrok_auth)
    except Exception as e:
        st.warning(f"Error setting Ngrok Auth Token: {e}")
else:
    st.warning("⚠️ No `NGROK_AUTHTOKEN` found in environment. Ngrok might expire sessions or fail. Set this token in Streamlit Secrets!")

# Initialize Data if DB is missing (Streamlit Cloud runs fresh containers)
db_path = os.path.join(os.getcwd(), 'Phase1_DataIngestion', 'restaurants.db')
if not os.path.exists(db_path):
    st.info("Generating initial SQLite Database, this might take a moment...")
    try:
        # Run Data loader synchronously to make sure the db is there
        subprocess.run([sys.executable, "Phase1_DataIngestion/data_loader.py"], check=True)
        st.success("Database regenerated successfully.")
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to load dataset: {e}")

# Launch FastAPI using a persistent connection
if 'fastapi_process' not in st.session_state:
    st.info("Starting up FastAPI Server on internal port 8000...")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "Phase2_BackendAPI.main:app", "--host", "0.0.0.0", "--port", "8000"],
        env=env
    )
    st.session_state.fastapi_process = process
    time.sleep(3)

# Setup Ngrok Tunnel
if 'tunnel_url' not in st.session_state:
    st.info("Creating Ngrok Public Tunnel...")
    try:
        # Open a tunnel on port 8000
        http_tunnel = ngrok.connect(8000)
        st.session_state.tunnel_url = http_tunnel.public_url
    except Exception as e:
        st.error(f"Failed to create tunnel: {e}")

if 'tunnel_url' in st.session_state:
    st.success("✅ Your Backend is Live!")
    public_url = st.session_state.tunnel_url
    
    st.markdown("### Next.js Vercel Configuration")
    st.write("Copy the following URL into your Vercel Environment variables as `NEXT_PUBLIC_BACKEND_URL`:")
    st.code(public_url, language="bash")
    
    st.markdown("### Test the public API directly via Ngrok:")
    st.markdown(f"**[Click Here for MetaData Endpoint]({public_url}/api/metadata)**")
    
    st.write("---")
    try:
        res = requests.get("http://localhost:8000/api/metadata", timeout=5)
        if res.status_code == 200:
            st.write("Internal Status: Healthy ✔️")
    except Exception as e:
        st.error(f"Internal Health Fail: {e}")
