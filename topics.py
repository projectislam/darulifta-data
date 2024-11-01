import csv
import os
import json
import requests
from bs4 import BeautifulSoup
from time import sleep

def get_soup(url, retries=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} - Error fetching URL {url}: {e}")
            sleep(2)  # wait before retrying
    print(f"Failed to fetch URL {url} after {retries} attempts.")
    return None

def extract_topics(url, parent=None):
    visited_links = set()
    queue = [(url, parent)]  # Track each URL with its parent reference

    while queue:
        current_url, parent = queue.pop(0)
        if current_url in visited_links:
            continue
        visited_links.add(current_url)
        
        print(f"Visiting: {current_url}")
        soup = get_soup(current_url, retries=3)
        if not soup:
            print(f"Skipping {current_url} after multiple failed attempts.")
            if parent:
                parent[-1]["is_end"] = True
            continue

        ul = soup.select_one("body > div > section.bg-gray-50 > div > div.col-span-2 > div > ul") or \
             soup.select_one("body > div > main > div > ul")

        current_topics = []  # This will hold the child topics for the current URL
        if ul:
            for li in ul.find_all("li"):
                a = li.find("a")
                if a and a['href']:
                    title = a.get_text(strip=True)
                    topic_url = a['href']
                    if not topic_url.startswith("http"):
                        topic_url = requests.compat.urljoin(current_url, topic_url)

                    # Create the topic structure
                    topic = {
                        "title": title,
                        "url": topic_url,
                        "child": []
                    }

                    # Append the topic as a child of the current topic
                    current_topics.append(topic)

                    # Add the topic URL to the queue with a reference to its child list
                    queue.append((topic_url, topic["child"]))
            
            # Add collected topics as children of the parent topic
            if parent is not None:
                parent[-1]["child"] = current_topics
            else:
                parent = current_topics  # Root-level topics
        else:
            # If no child topics found, mark as `is_end`
            if parent:
                parent[-1]["is_end"] = True
                print(f"No subtopics found for {current_url}, marking as end.")

        # sleep(3)

    return parent  # Return the entire topic structure

def process_csv():
    with open("./madaras/madaras.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            madrasa_name = row["Link"].rstrip('/').split('/')[-1]
            madrasa_folder = f"./{madrasa_name}"
            os.makedirs(madrasa_folder, exist_ok=True)
            
            print(f"Processing Madrasa: {madrasa_name}")
            topics = extract_topics(row["Link"])

            data = {
                "madrasa": madrasa_name,
                "topics": topics
            }
            with open(f"{madrasa_folder}/topics.json", "w", encoding="utf-8") as jsonfile:
                json.dump(data, jsonfile, ensure_ascii=False, indent=4)
            print(f"Saved topics for {madrasa_name} in {madrasa_folder}/topics.json\n")

if __name__ == "__main__":
    process_csv()
