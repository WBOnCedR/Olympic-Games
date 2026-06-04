import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm 
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load the dataset of modern Olympic athletes
df_modern = pd.read_csv("../Data/olympic_athletes.csv")

# Extract names and URLs of athletes
names = df_modern['athlete_full_name'].tolist()
urls = df_modern['athlete_url'].tolist()  

# Function to scrape Sex, Height, Weight and NOC information from Olympedia
def get_athlete_info(full_name):
    """
    Get Sex, Height, Weight and NOC of an athlete from Olympedia.

    full_name: string, for example "Michael Phelps"
    output: dict {"Sex": ..., "Height": ..., "Weight": ..., "NOC": ..., "NOC_code": ...}
            or None if not found
    """
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # GET homepage for authenticity_token
    home_url = "https://www.olympedia.org/"
    home_resp = session.get(home_url, headers=headers)
    home_soup = BeautifulSoup(home_resp.text, "html.parser")

    token_input = home_soup.find("input", {"name": "authenticity_token"})
    token = token_input["value"] if token_input else None
    
    # POST search in /athletes/quick_search
    search_url = "https://www.olympedia.org/athletes/quick_search"
    payload = {"query": full_name, "commit": "Go"}
    if token:
        payload["authenticity_token"] = token
    
    search_resp = session.post(search_url, data=payload, headers=headers)
    search_soup = BeautifulSoup(search_resp.text, "html.parser")

    # Get the first athlete of the table (best match)
    table = search_soup.find("table", class_="table-striped")
    if not table:
        return None
    
    first_row = table.find("tbody").find("tr")
    athlete_link_tag = first_row.find("a", href=True)
    if not athlete_link_tag:
        return None
    
    athlete_url = "https://www.olympedia.org" + athlete_link_tag["href"]
    
    # Get athlete page
    athlete_resp = session.get(athlete_url, headers=headers)
    athlete_soup = BeautifulSoup(athlete_resp.text, "html.parser")
    
    biodata_table = athlete_soup.find("table", class_="biodata")
    if not biodata_table:
        return None
    
    info = {"Sex": None, "Height": None, "Weight": None, "NOC": None, "NOC_code": None}
    
    for row in biodata_table.find_all("tr"):
        th = row.find("th").text.strip()
        td = row.find("td")
        if not td:
            continue
        td_text = td.text.strip()
        
        if th == "Sex":
            info["Sex"] = td_text
        elif th == "Measurements":
            parts = td_text.split("/")
            if len(parts) == 2:
                info["Height"] = parts[0].strip()
                info["Weight"] = parts[1].strip()
        elif th == "NOC":
            link = td.find("a")
            if link:
                info["NOC"] = link.text.strip()
                href = link.get("href", "")
                if "/countries/" in href:
                    info["NOC_code"] = href.split("/")[-1]
            else:
                info["NOC"] = td_text
    
    return info

# Parameters
batch_size = 300
max_threads = 5
sleep_between_requests = 0.1
max_retries = 3

# Function to scrape athlete data with retry
def scrape_athlete(name, url):
    """
    Scrape athlete info with automatic retry.
    Includes the athlete URL from the original dataset.
    """
    for attempt in range(max_retries):
        try:
            info = get_athlete_info(name)
            if info is None:
                info = {"Sex": None, "Height": None, "Weight": None, "NOC": None, "NOC_code": None}
            
            return {
                "athlete_full_name": name,
                "athlete_url": url,  
                "sex": info["Sex"],
                "height": info["Height"],
                "weight": info["Weight"],
                "NOC": info["NOC"],
                "NOC_code": info["NOC_code"]
            }
        except Exception:
            time.sleep(1)  # Wait before retrying

    # If all retries fail, return None values
    return {"athlete_full_name": name, "athlete_url": url, "sex": None, "height": None, "weight": None, "NOC": None, "NOC_code": None}

# List to store results
results = []

# Loop over athletes in batches to avoid memory issues
for i in range(0, len(names), batch_size):
    batch_df = df_modern.iloc[i:i+batch_size]
    batch_names_urls = list(zip(batch_df['athlete_full_name'], batch_df['athlete_url']))

    print(f"Processing batch {i//batch_size + 1} / {(len(names)-1)//batch_size + 1} ...")

    # Parallelize requests using ThreadPoolExecutor
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(scrape_athlete, name, url): name for name, url in batch_names_urls}

        # Collect results as they complete, with a progress bar
        for future in tqdm(as_completed(futures), total=len(futures), desc="Athletes in batch"):
            results.append(future.result())
            time.sleep(sleep_between_requests)

    # Update CSV progressively
    pd.DataFrame(results).to_csv("olympia_athletes_bio_parallel.csv", index=False)

print("Done! CSV updated: olympia_athletes_bio_parallel.csv")
