import requests
from bs4 import BeautifulSoup
import re
import json
import os

# --------------------- [1] Get Cookie ---------------------

def get_cookie():
    try:
        with open("cookies.json", "r") as f:
            return json.load(f).get("sp_dc", "")
    except:
        return ""

# --------------------- [2] Get Latest Saved Pin ---------------------

def get_latest_pin(username, sess_cookie):
    url = f"https://www.pinterest.com/{username}/_saved/"
    headers = {"User-Agent": "Mozilla/5.0"}
    cookies = {"_pinterest_sess": sess_cookie}

    try:
        print(f"🔐 Scraping {username} with cookie...")
        res = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        if res.status_code != 200:
            print(f"❌ Request failed: {res.status_code}")
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        scripts = soup.find_all("script")

        for script in scripts:
            if "pinimg.com/originals" in script.text:
                match = re.search(r'https://i\.pinimg\.com/originals/[^"]+', script.text)
                if match:
                    image_url = match.group(0)
                    return {
                        "image": image_url,
                        "title": "Pinterest Pin",
                        "link": url
                    }

        print("⚠️ No pin found")
        return None

    except Exception as e:
        print(f"❌ Scraper error:", e)
        return None

# --------------------- [3] Validate Pinterest Cookie ---------------------

def validate_cookie(cookie):
    url = "https://www.pinterest.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    cookies = {"_pinterest_sess": cookie}

    try:
        res = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        return "Logout" in res.text or "Saved" in res.text  # crude check
    except:
        return False

# --------------------- [4] Validate Pinterest Username ---------------------

def validate_username(username, cookie):
    url = f"https://www.pinterest.com/{username}/_saved/"
    headers = {"User-Agent": "Mozilla/5.0"}
    cookies = {"_pinterest_sess": cookie}

    try:
        res = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        return res.status_code == 200 and "pinimg.com" in res.text
    except:
        return False
