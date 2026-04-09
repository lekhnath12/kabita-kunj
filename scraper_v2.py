import requests
from bs4 import BeautifulSoup
import re
import time
import json
from collections import deque

def crawl_round_robin(start_urls, max_total_pages=100):
    unique_vocab = set()
    visited_links = set()
    
    # Create a dictionary where each key is a portal and each value is a deque (queue)
    # This allows us to track links for each site independently
    portal_queues = {url: deque([url]) for url in start_urls}
    portal_list = list(start_urls)
    
    nepali_pattern = re.compile(r'[\u0900-\u097F]+')
    digit_pattern = re.compile(r'[\u0966-\u096F0-9\u0964]')
    
    pages_crawled = 0
    portal_index = 0 # To track whose turn it is

    print(f"--- Starting Round Robin Crawl across {len(start_urls)} portals ---")

    while pages_crawled < max_total_pages and any(portal_queues.values()):
        # 1. Determine whose turn it is
        current_base = portal_list[portal_index]
        current_queue = portal_queues[current_base]

        # Move to the next portal index for the next iteration (Round Robin)
        portal_index = (portal_index + 1) % len(portal_list)

        # 2. If the current portal has no more links, skip to the next
        if not current_queue:
            continue
            
        url = current_queue.popleft()
        if url in visited_links:
            continue
            
        try:
            # Polite delay
                        
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            visited_links.add(url)
            
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 3. Extract Words
            text = soup.get_text()
            found_words = nepali_pattern.findall(text)
            for w in found_words:
                if not digit_pattern.search(w) and len(w) > 1:
                    unique_vocab.add(w)

            # 4. Find internal links and add them ONLY to this portal's specific queue
            for a_tag in soup.find_all('a', href=True):
                link = a_tag['href']
                if link.startswith('/') or current_base in link:
                    full_link = link if link.startswith('http') else current_base.rstrip('/') + link
                    if full_link not in visited_links:
                        portal_queues[current_base].append(full_link)

            pages_crawled += 1
            print(f"[{pages_crawled}] Turn: {current_base} | Scraped: {url} | Total Vocab: {len(unique_vocab)}")

        except Exception as e:
            print(f"Skipping {url} due to error.")

    return list(unique_vocab)

# --- EXECUTION ---

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
    
    # Technology & Niche
    "https://www.techpana.com",
    "https://ictframe.com",
    "https://www.sajhasabal.com",
    "https://www.nepallive.com",
    "https://shilapatra.com",
    "https://healthaawaj.com"
]


# Run the round-robin scraper
voc = json.load(open(r"C:\Users\lekhp\OneDrive\Desktop\clean_nepali_words.json", encoding="utf-8"))


new_words = crawl_round_robin(news_portals, max_total_pages=1000)
voc += new_words
voc = list(set(voc)) # Remove duplicates

# Save results as before
with open("clean_nepali_words.json", "w", encoding="utf-8") as f:
    json.dump(voc, f, ensure_ascii=False, indent=2)