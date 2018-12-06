"""
"""

import requests
import sys

sparkline = r"https://web.archive.org/__wb/sparkline"
calendar = r"https://web.archive.org/__wb/calendarcaptures"

url = sys.argv[1]

years = requests.get(sparkline, params={"url": url, "output": "json"}).json()["years"]

for year in sorted(years):

    print("year:", year, file=sys.stderr)

    months = requests.get(calendar, params={"url": url, "selected_year": year}).json()

    for month in months:
        for week in month:
            for day in week:
                if day and (day["st"][0] == 200):
                    print(day["ts"][0])

