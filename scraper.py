import requests
from bs4 import BeautifulSoup
import re
import time
import json

import re

def process_nepali_word(word):
    # Pattern to capture syllables with leading half-consonants
    # This groups (Consonant + Halanta)* + (Base Consonant/Vowel) + (Matra)
    syllable_pattern = r'(?:[अ-ह]्)*[अ-ह]़?[\u093e-\u094c]?|[अ-औ]'
    
    # 1. Extract syllables
    syllables = re.findall(syllable_pattern, word)
    
    # 2. Define Plural (Long/S) markers
    plural_markers = r'[आईऊएऐओऔाीूेैोौंः]'
    
    weights = ""
    for syl in syllables:
        if re.search(plural_markers, syl):
            weights += "S"
        else:
            weights += "l"
            
    return syllables, weights
# --- LOGIC FROM PREVIOUS STEPS ---

def crawl_and_scrape_vocabulary(start_urls, max_pages=50):
    unique_vocab = [] 
    visited_links = set()
    nepali_pattern = re.compile(r'[\u0900-\u097F]+')
    digit_pattern = re.compile(r'[\u0966-\u096F0-9\u0964]') # Includes Purna Viram

    for base_url in start_urls:
        pages_crawled = 0
        queue = [base_url]
        
        print(f"\n--- Starting Crawl: {base_url} ---")
        
        while queue and pages_crawled < max_pages:
            url = queue.pop(0)
            if url in visited_links: continue
            
            try:
                response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                visited_links.add(url)
                if response.status_code != 200: continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 1. Extract Words from Current Page
                text = soup.get_text()
                words = nepali_pattern.findall(text)
                words = [x for x in words if not digit_pattern.search(x)]
                unique_vocab += words
                                
                # 2. Find internal links to follow
                for a_tag in soup.find_all('a', href=True):
                    link = a_tag['href']
                    # Ensure link is internal and looks like a news article
                    if link.startswith('/') or base_url in link:
                        full_link = link if link.startswith('http') else base_url.rstrip('/') + link
                        if full_link not in visited_links:
                            queue.append(full_link)
                
                pages_crawled += 1
                print(f"[{pages_crawled}] Scraped: {url} | Vocab size: {len(unique_vocab)}")
                time.sleep(1) # Be polite to the server
                
            except Exception as e:
                print(f"Skipping {url} due to error.")
                
    return unique_vocab

# --- RUNNING THE CRAWLER ---





# Target portals
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


for news_portal in news_portals[6:7]:
    vocabulary_data = json.load(open("clean_nepali_words.json", "r", encoding="utf-8"))
    vocabulary_data_new = crawl_and_scrape_vocabulary([news_portal], max_pages=5)
    vocabulary_data += vocabulary_data_new
    vocabulary_data = list(set(vocabulary_data))

    with open("clean_nepali_words.json", "w", encoding="utf-8") as f:
        json.dump(vocabulary_data, f, ensure_ascii=False)
    print(f"--- Completed: {news_portal} | Total Vocab Size: {len(vocabulary_data)} ---\n")