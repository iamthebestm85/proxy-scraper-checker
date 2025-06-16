import requests
import time

OUTPUT_FILE = "proxies.txt"
RETRIES = 3
SLEEP_BETWEEN = 1  # seconds

# ✅ Both ProxyScrape URLs
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
]

def fetch_proxies_from_url(url, retries=RETRIES):
    for attempt in range(1, retries + 1):
        try:
            print(f"🌐 Fetching from: {url} (Attempt {attempt})")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            proxies = [line.strip() for line in response.text.splitlines() if ":" in line]
            if proxies:
                return proxies
            else:
                print("⚠️ No proxies received. Retrying...")
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(SLEEP_BETWEEN)
    print(f"❌ Failed to fetch from: {url}")
    return []

def save_proxies(proxy_list, filename=OUTPUT_FILE):
    unique = sorted(set(proxy_list))
    with open(filename, 'w') as f:
        for proxy in unique:
            f.write(proxy + "\n")
    print(f"\n✅ Saved {len(unique)} proxies to '{filename}'")

def main():
    all_proxies = []
    for url in PROXY_SOURCES:
        proxies = fetch_proxies_from_url(url)
        print(f"📥 Retrieved {len(proxies)} proxies")
        all_proxies.extend(proxies)
    
    save_proxies(all_proxies)

if __name__ == "__main__":
    main()
