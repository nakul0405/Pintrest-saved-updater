import requests
from bs4 import BeautifulSoup
import re

def get_latest_pin(username):
    url = f"https://www.pinterest.com/{username}/_saved/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        print(f"🔍 Scraping: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"❌ Failed to fetch page, status: {res.status_code}")
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        # Pinterest has multiple <script> tags containing JSON data
        scripts = soup.find_all("script")

        for script in scripts:
            if "pinimg.com/originals" in script.text:
                # Find image URL using regex
                match = re.search(r'https://i\.pinimg\.com/originals/[^"]+', script.text)
                if match:
                    image_url = match.group(0)
                    print(f"🖼️ Found image: {image_url}")
                    return {
                        "image": image_url,
                        "title": "Pinterest Pin",
                        "link": url
                    }

        print("⚠️ No valid image pin found.")
        return None

    except Exception as e:
        print(f"❌ Error scraping: {e}")
        return None
