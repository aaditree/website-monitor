import streamlit as st  # type: ignore
import requests # type: ignore
import hashlib
import time
import base64
import datetime

st.set_page_config(page_title="Website Monitor", layout="centered")

def get_video_base64(video_path):
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    return base64.b64encode(video_bytes).decode()

video_base64 = get_video_base64("cat.mp4")  

video_html = f"""
<style>
video {{
  position: fixed;
  top: 0;
  left: 0;
  min-width: 100vh;
  min-height: 100vh;
  z-index: -1;
}}
.stApp {{
  background: transparent;
}}
</style>

<video autoplay loop muted playsinline>
  <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
</video>
"""

st.markdown(video_html, unsafe_allow_html=True)
st.markdown('<div class="overlay">', unsafe_allow_html=True)
ll=[]
st.title("Website Monitor")
number_of_websites = st.number_input("How many websites do you want to monitor?", 0)
for i in range(0,number_of_websites):
    ll.append(st.text_input("Enter the website URL to monitor",key=f"url_input_{i}"))
check_interval = st.slider("Check interval (in seconds)", 30, 3600, 300)
start_button = st.button("Start Monitoring")

def get_hash(url):
    response = requests.get(url)
    return hashlib.md5(response.text.encode('utf-8')).hexdigest()

if start_button:
    for url in ll:
        prev_hash = get_hash(url)
        st.success("Monitoring started...")

        while True:
            time.sleep(check_interval)
            current_hash = get_hash(url)
            if current_hash != prev_hash:
                current_time  = datetime.datetime.now()
                st.success(f"Change detected on {url} at {current_time}!")
                prev_hash = current_hash
            else:
                st.info("No change detected.")