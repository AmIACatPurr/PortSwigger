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
