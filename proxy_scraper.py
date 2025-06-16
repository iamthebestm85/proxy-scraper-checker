import requests
import time

OUTPUT_FILE = "proxies.txt"
RETRIES = 3
SLEEP_BETWEEN = 1  # seconds
PROXY_SOURCES = [
    # ProxyScrape (HTTP proxies)
    "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",

    # Free Proxy List (Plain text)
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    
    # Proxy-List.Download (HTTP proxies)
    "https://www.proxy-list.download/api/v1/get?type=http",
    
    # GitHub - Useragentstring-com proxy list
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",

    # GitHub - Monosans proxies
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
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
