import requests
from bs4 import BeautifulSoup
import re
import json
import os

def get_cookie():
    try:
        with open("cookies.json", "r") as f:
            return json.load(f).get("sp_dc", "")
    except:
        return ""

def get_latest_pin(username):
    url = f"https://www.pinterest.com/{username}/_saved/"
    sp_dc = get_cookie()

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    cookies = {
        "sp_dc": sp_dc
    }

    try:
        print(f"🔐 Scraping with cookie: {url}")
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

        print("⚠️ No image pin found")
        return None

    except Exception as e:
        print(f"❌ Scraper error:", e)
        return None
