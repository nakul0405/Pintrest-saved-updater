import requests
from bs4 import BeautifulSoup

def get_latest_pin(username):
    url = f"https://www.pinterest.com/{username}/_saved/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        img_tags = soup.find_all("img", {"src": True})

        for img in img_tags:
            img_url = img["src"]
            if "pinimg.com" in img_url:
                return {
                    "image": img_url,
                    "title": "Pinterest Pin",
                    "link": url
                }
    except Exception as e:
        print("Error scraping:", e)
    return None
