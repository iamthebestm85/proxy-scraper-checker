import aiohttp
import asyncio
import os
import re
import time
from tqdm import tqdm

# Configuration
PROXY_FILE = "proxies.txt"  # Input file with proxies (ip:port per line)
OUTPUT_DIR = "working_proxies"  # Directory to save working proxies
MAX_THREADS = 50  # Concurrent requests (adjust based on system/API limits)
TIMEOUT = 5  # Timeout for proxy checks in seconds
PROXY_CHECK_API = "http://proxycheck.io/v2"  # External API for SOCKS checks
TEST_URLS = {
    "http": "http://httpbin.org/ip",
    "https": "https://httpbin.org/ip",
    "socks4": "http://httpbin.org/ip",
    "socks5": "http://httpbin.org/ip"
}

# Create output directory if it doesn’t exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

async def check_proxy_async(proxy, protocol, session):
    """Check if a proxy works for a given protocol asynchronously."""
    try:
        if protocol in ["http", "https"]:
            proxies = {protocol: f"{protocol}://{proxy}"}
            async with session.get(TEST_URLS[protocol], proxy=proxies[protocol], timeout=TIMEOUT) as response:
                return response.status == 200
        else:
            ip, port = proxy.split(":")
            async with session.get(
                f"{PROXY_CHECK_API}/{ip}?port={port}&vpn=1&asn=1",
                timeout=TIMEOUT,
                headers={"Accept": "application/json"}
            ) as response:
                data = await response.json()
                data = data.get(ip, {})
                return data.get("proxy") == "yes" and data.get("type", "").lower() == protocol
    except Exception:
        return False

async def check_proxy_all_protocols_async(proxy, session):
    """Check a proxy for all protocols asynchronously."""
    results = {}
    for protocol in ["http", "https", "socks4", "socks5"]:
        results[protocol] = await check_proxy_async(proxy, protocol, session)
    return results

def write_working_proxies(protocol, proxies):
    """Write working proxies to a file."""
    if proxies:
        filename = os.path.join(OUTPUT_DIR, f"{protocol}_working.txt")
        with open(filename, "a", encoding="utf-8") as f:
            for proxy in proxies:
                f.write(f"{proxy}\n")

async def main_async():
    """Main async function to process proxies."""
    # Read proxies from file
    try:
        with open(PROXY_FILE, "r", encoding="utf-8") as f:
            proxies = [
                line.strip() for line in f
                if line.strip() and re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$", line.strip())
            ]
    except FileNotFoundError:
        print(f"Error: {PROXY_FILE} not found. Please create a file named 'proxies.txt' with IP:port per line.")
        return {}
    except Exception as e:
        print(f"Error reading {PROXY_FILE}: {e}")
        return {}

    total_proxies = len(proxies)
    if total_proxies == 0:
        print("No valid proxies found in the file (format: IP:port per line).")
        return {}

    print(f"Checking {total_proxies} proxies...")

    # Collect working proxies in memory
    working_proxies = {"http": [], "https": [], "socks4": [], "socks5": []}

    # Async session with timeout
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        semaphore = asyncio.Semaphore(MAX_THREADS)

        async def check_with_semaphore(proxy):
            async with semaphore:
                return await check_proxy_all_protocols_async(proxy, session)

        # Create and run tasks with progress tracking
        tasks = [check_with_semaphore(proxy) for proxy in proxies]
        results = []
        for future in tqdm(asyncio.as_completed(tasks), total=total_proxies, desc="Checking proxies"):
            result = await future
            results.append(result)

        # Process results
        for proxy, result in zip(proxies, results):
            for protocol, is_working in result.items():
                if is_working:
                    working_proxies[protocol].append(proxy)
                    print(f"Working {protocol.upper()} proxy: {proxy}")

    # Write results to files
    for protocol, proxies_list in working_proxies.items():
        write_working_proxies(protocol, proxies_list)

    # Return summary data
    return {
        "total_proxies": total_proxies,
        "working_proxies": {protocol: len(proxies_list) for protocol, proxies_list in working_proxies.items()}
    }

def main():
    """Main function to run the async proxy checker."""
    start_time = time.time()
    summary = asyncio.run(main_async())
    duration = time.time() - start_time

    if summary:
        proxies_per_second = summary["total_proxies"] / duration if duration > 0 else 0
        print("\n### Proxy Check Summary ###")
        print(f"Total Proxies Checked: {summary['total_proxies']}")
        for protocol, count in summary["working_proxies"].items():
            print(f"Working {protocol.upper()} Proxies: {count}")
        print(f"Results saved in '{OUTPUT_DIR}' directory.")
        print(f"Completed in {duration:.2f} seconds")
        print(f"Proxies checked per second: {proxies_per_second:.2f}")

if __name__ == "__main__":
    main()