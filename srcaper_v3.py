import requests
from bs4 import BeautifulSoup
import re
import time
import json
from collections import deque

def crawl_round_robin(start_urls, max_total_pages=100, save_path="clean_nepali_words.json"):
    # Load existing data at the start to ensure we are appending, not overwriting
    try:
        with open(save_path, "r", encoding="utf-8") as f:
            unique_vocab = set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        unique_vocab = set()

    visited_links = set()
    portal_queues = {url: deque([url]) for url in start_urls}
    portal_list = list(start_urls)
    
    nepali_pattern = re.compile(r'[\u0900-\u097F]+')
    digit_pattern = re.compile(r'[\u0966-\u096F0-9\u0964]')
    
    pages_crawled = 0
    portal_index = 0 

    print(f"--- Starting Round Robin Crawl across {len(start_urls)} portals ---")

    while pages_crawled < max_total_pages and any(portal_queues.values()):
        current_base = portal_list[portal_index]
        current_queue = portal_queues[current_base]
        portal_index = (portal_index + 1) % len(portal_list)

        if not current_queue:
            continue
            
        url = current_queue.popleft()
        if url in visited_links:
            continue
            
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            visited_links.add(url)
            
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            found_words = nepali_pattern.findall(text)
            for w in found_words:
                if not digit_pattern.search(w) and len(w) > 1:
                    unique_vocab.add(w)

            for a_tag in soup.find_all('a', href=True):
                link = a_tag['href']
                if link.startswith('/') or current_base in link:
                    full_link = link if link.startswith('http') else current_base.rstrip('/') + link
                    if full_link not in visited_links:
                        portal_queues[current_base].append(full_link)

            pages_crawled += 1
            
            # --- Save every 100 URLs inside the function ---
            if pages_crawled % 10 == 0:
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(sorted(list(unique_vocab)), f, ensure_ascii=False)
                print(f"--- AUTO-SAVE: File updated at {pages_crawled} URLs --- with unique words {len(unique_vocab)}")

        except Exception as e:
            print(f"Skipping {url} due to error: {e}")

    # Final save before exiting the function
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(sorted(list(unique_vocab)), f, ensure_ascii=False, indent=2)
    
    return list(unique_vocab)

# --- Main Execution ---
news_portals = [
    # General / Mainstream
    "https://www.onlinekhabar.com",
    "https://www.ratopati.com",
    "https://www.setopati.com",
    "https://ekantipur.com",
    "https://www.nagariknetwork.com",
    "https://annapurnapost.com",
    "https://www.nayapatrikadaily.com",
    "https://www.ujyaaloonline.com",
    "https://lokaantar.com",

    
    "https://www.khabarhub.com",
    "https://www.himalpress.com",
    "https://www.himalkhabar.com",
    "https://deshsanchar.com",
    
    # State-Owned / Official
    "https://gorkhapatraonline.com",
    "https://onlineradionepal.gov.np",
    "https://ntv.org.np",
    
    # Business & Economy
    "https://www.karobardaily.com",
    "https://www.arthabeat.com",
    "https://bizshala.com",
    "https://merolagani.com",
    "https://bizpati.com",
    "https://arthasarathi.com",
    
    # # Technology & Niche
    "https://www.techpana.com",
    "https://ictframe.com",
    "https://www.sajhasabal.com",
    "https://www.nepallive.com",
    "https://shilapatra.com",
    "https://healthaawaj.com"
]


# Note: Update 'path_to_file' if you want
# Note: Update 'path_to_file' if you want to use the specific OneDrive path
path_to_file = "clean_nepali_words.json" 

crawl_round_robin(news_portals, max_total_pages=1000000, save_path=path_to_file)