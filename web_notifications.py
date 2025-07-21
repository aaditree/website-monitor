import streamlit as st # type: ignore
import requests
import hashlib
import threading
import time
import datetime
import base64
from selenium import webdriver # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from webdriver_manager.chrome import ChromeDriverManager# type: ignore

def get_video_base64(video_path):
    with open(video_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def take_screenshot(url, filename="screenshot.png"):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(url)
    time.sleep(3)
    driver.save_screenshot(filename)
    driver.quit()
    return filename

def get_hash(url):
    try:
        response = requests.get(url, timeout=10)
        return hashlib.md5(response.text.encode("utf-8")).hexdigest()
    except Exception as e:
        return None

def monitor_site(url, interval, container):
    prev_hash = get_hash(url)
    while True:
        time.sleep(interval)
        current_hash = get_hash(url)
        if current_hash is None or prev_hash is None:
            continue
        if current_hash != prev_hash:
            prev_hash = current_hash
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            screenshot = take_screenshot(url)
            with container:
                st.success(f"🔁 Change detected on {url} at {timestamp}")
                st.image(screenshot, caption=f"{url} at {timestamp}")
        else:
            with container:
                st.info(f"✅ No change on {url} as of {datetime.datetime.now().strftime('%H:%M:%S')}")

st.set_page_config(page_title="Website Monitor", layout="centered")

video_base64 = get_video_base64("cat.mp4")
video_html = f"""
<style>
video {{
  position: fixed;
  top: 0;
  left: 0;
  min-width: 100vw;
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

st.title("Website Change Monitor with Screenshot")

website_count = st.number_input("How many websites do you want to monitor?", min_value=1, max_value=10, step=1)
urls = []
for i in range(website_count):
    url = st.text_input(f"Enter URL #{i + 1}", key=f"url_{i}")
    urls.append(url)

check_interval = st.slider("Check every (seconds)", min_value=30, max_value=3600, value=300, step=30)

start = st.button("Start Monitoring")

if start:
    st.success("Monitoring started in background. You'll see updates here.")
    for url in urls:
        if url:
            container = st.container()
            thread = threading.Thread(target=monitor_site, args=(url, check_interval, container), daemon=True)
            thread.start()
